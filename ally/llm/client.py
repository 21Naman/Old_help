"""One way to call the model: `structured()` → a validated Pydantic object, or LLMError.

The model is reached through LiteLLM, so any provider it supports works by changing one env var:
`groq/llama-3.3-70b-versatile` (default), `gemini/gemini-2.5-flash`, `ollama/llama3.1` and so on.
Provider keys are read from the environment (GROQ_API_KEY, GEMINI_API_KEY).

Two layers of resilience sit under the one call:

1. LiteLLM retries transient errors (rate limits, 5xx, timeouts) against the same provider.
2. LLM_FALLBACK_MODEL re-runs the whole turn on a second provider when the first one fails,
   including when it returns output that doesn't fit the schema.

There is deliberately no fallback *text*. If both fail the API returns an explicit error and the
UI shows it; nothing pretends to be the model.
"""

from __future__ import annotations

import time
from typing import Any, Sequence, TypeVar

from pydantic import BaseModel
from strands import Agent
from strands.models.litellm import LiteLLMModel

from config import LLM_FALLBACK_MODEL, LLM_MAX_TOKENS, LLM_TIMEOUT_S, llm_model_for
from core.errors import LLMError
from core.log import log, metric

T = TypeVar("T", bound=BaseModel)


def _model(model_id: str, temperature: float) -> LiteLLMModel:
    return LiteLLMModel(
        client_args={"num_retries": 2, "timeout": LLM_TIMEOUT_S},
        model_id=model_id,
        params={"temperature": temperature, "max_tokens": LLM_MAX_TOKENS},
    )


def finish_instruction(model: type[BaseModel]) -> str:
    return f"\n\nWhen you are done, finish by calling the {model.__name__} tool exactly once."


async def structured(
    task: str,
    system: str,
    prompt: str,
    output: type[T],
    *,
    tools: Sequence[Any] = (),
    hooks: Sequence[Any] = (),
    invocation_state: dict[str, Any] | None = None,
    max_turns: int = 4,
    temperature: float = 0.2,
) -> T:
    """Run a fresh agent (agents are not safe to share across concurrent requests)."""

    async def run(model_id: str) -> T:
        agent = Agent(
            model=_model(model_id, temperature),
            system_prompt=system + finish_instruction(output),
            tools=list(tools),
            hooks=list(hooks),
            callback_handler=None,
        )
        result = await agent.invoke_async(
            prompt,
            structured_output_model=output,
            invocation_state=dict(invocation_state or {}),
            limits={"turns": max_turns},
        )
        parsed = result.structured_output
        if parsed is None or not isinstance(parsed, output):
            raise ValueError(f"no structured output (stop_reason={result.stop_reason})")
        _record(task, started, ok=True, usage=_usage(result), model=model_id)
        return parsed

    started = time.perf_counter()
    primary = llm_model_for(task)
    try:
        return await run(primary)
    except Exception as exc:  # providers raise their own error types; any failure may be provider-shaped
        _record(task, started, ok=False, error=exc, model=primary)
        if not LLM_FALLBACK_MODEL or LLM_FALLBACK_MODEL == primary:
            raise LLMError("Ally is having trouble thinking right now.", detail=f"{task}: {exc!r}") from exc
        log("llm_failover", task=task, frm=primary, to=LLM_FALLBACK_MODEL, error=str(exc))
        metric("LLMFailover", 1, "Count", Task=task)
    try:
        return await run(LLM_FALLBACK_MODEL)
    except Exception as exc:
        _record(task, started, ok=False, error=exc, model=LLM_FALLBACK_MODEL)
        raise LLMError("Ally is having trouble thinking right now.", detail=f"{task}: {exc!r}") from exc


def _usage(result: Any) -> dict[str, Any]:
    try:
        return dict(result.metrics.accumulated_usage)
    except Exception:
        return {}


def _record(
    task: str,
    started: float,
    *,
    ok: bool,
    model: str,
    error: Any = None,
    usage: dict[str, Any] | None = None,
) -> None:
    ms = round((time.perf_counter() - started) * 1000)
    metric("LLMLatency", ms, "Milliseconds", Task=task)
    if not ok:
        metric("LLMError", 1, "Count", Task=task)
        log("llm_error", task=task, model=model, ms=ms, error=str(error))
    else:
        log("llm_ok", task=task, model=model, ms=ms, usage=usage or {})
