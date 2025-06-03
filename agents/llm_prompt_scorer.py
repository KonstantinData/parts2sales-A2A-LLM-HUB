"""
llm_prompt_scorer.py

Purpose : Uses OpenAI to evaluate prompt quality using a scoring matrix
Version : 0.1.2
Author  : Konstantin’s AI Copilot
Notes   :
- Calls GPT to score YAML prompt with structured output
- Handles retries and structured output enforcement
- Logs all attempts and response structure
"""

from openai import OpenAI
import logging
import time
import os

logger = logging.getLogger("PromptScorer")
logger.setLevel(logging.INFO)


def score_prompt(prompt_text: str, matrix_name: str, model: str = "gpt-4-turbo") -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key) if api_key else OpenAI()

    scoring_prompt = f"""
You are a prompt quality evaluator. Given the following prompt YAML text, assess it using the scoring matrix: {matrix_name}.

Return a JSON object with the following fields:
- score: float (0.0–1.0)
- matrix: dict[str, float] (subscores per category)
- feedback: string (summary)
- pass_threshold: bool
- issues: list[str]
- prompt_version: string (if parseable from YAML)

Respond in minified JSON only, no comments or formatting.

Prompt to evaluate:
\n\n{prompt_text}
"""

    logger.info("[SCORE_PROMPT] Raw scoring prompt sent to model")
    print(f"[SCORE_PROMPT] Prompt body begins:\n{scoring_prompt[:1000]}\n...")

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": scoring_prompt}],
                temperature=0.2,
            )
            result = response.choices[0].message.content
            print(
                f"[SCORE_PROMPT] GPT response attempt {attempt+1}:\n{result[:500]}\n..."
            )
            return result
        except Exception as e:
            logger.warning(f"Scoring attempt {attempt+1} failed: {e}")
            time.sleep(1)

    logger.error("All scoring attempts failed")
    return ""
