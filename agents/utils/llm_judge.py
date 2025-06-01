"""
llm_judge Utility

Central function for LLM-based evaluation tasks (prompt quality, output review, etc.).
Handles prompt formatting, LLM call, (optional) Redis cache, returns structured result.

Notes:
------
- Use this in all agents that need LLM-based scoring or qualitative review.
- Optionally, pass a cache (e.g., Redis) to avoid duplicate scoring (cost-efficient).
- Result always as LLMJudgeResult (ready for logging/event).
"""

from typing import Any, Dict, Optional
import hashlib
import json
from agents.utils.schemas import BaseModel, Field


class LLMJudgeResult(BaseModel):
    """
    Result of an LLM-based scoring or judging task.
    """

    score: float = Field(..., description="Final score (normalized 0..1)")
    explanation: str = Field(..., description="Short explanation or feedback from LLM")
    details: Dict[str, Any] = Field(
        default_factory=dict, description="Extra info (raw LLM output, debug, etc.)"
    )


def llm_judge(
    client,
    judge_prompt: str,
    eval_text: str,
    scoring_matrix: Dict[str, Any],
    cache=None,
    cache_ttl=86400,
    model="gpt-4o",
    temperature=0.0,
    **llm_kwargs,
) -> LLMJudgeResult:
    """
    Use LLM to judge a text against a prompt/scoring-matrix.
    Returns cached result if available.

    Args:
        client: OpenAI API client or compatible.
        judge_prompt: Prompt instructing the LLM how to evaluate.
        eval_text: The text (prompt, output, etc.) to be evaluated.
        scoring_matrix: Criteria, weights, dimensions, etc.
        cache: (Optional) Cache client (Redis).
        cache_ttl: Cache time (s).
        model: LLM model to use.
        temperature: LLM temperature.
        **llm_kwargs: Forwarded to client.

    Returns:
        LLMJudgeResult (score, explanation, details)
    """
    # Create a deterministic cache key
    cache_key = (
        "llmjudge:"
        + hashlib.sha256(
            (
                judge_prompt + eval_text + json.dumps(scoring_matrix, sort_keys=True)
            ).encode("utf-8")
        ).hexdigest()
    )
    # Check cache
    if cache and cache.exists(cache_key):
        cached = cache.get(cache_key)
        try:
            return LLMJudgeResult.parse_raw(cached)
        except Exception:
            pass  # ignore cache errors

    # Construct LLM messages
    messages = [
        {"role": "system", "content": judge_prompt},
        {"role": "user", "content": eval_text},
        # Optionally: add scoring_matrix as a separate message, if needed
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=500,
        **llm_kwargs,
    )
    # Parse LLM output (must be a JSON block with "score" and "explanation")
    try:
        out = json.loads(response.choices[0].message.content)
        result = LLMJudgeResult(
            score=float(out["score"]),
            explanation=out.get("explanation", ""),
            details=out,
        )
    except Exception as e:
        # Fallback: raw text as explanation, score -1
        result = LLMJudgeResult(
            score=-1.0,
            explanation=f"Parse error: {e}\nRaw: {response.choices[0].message.content}",
            details={},
        )

    # Cache result
    if cache:
        cache.set(cache_key, result.json(), ex=cache_ttl)
    return result
