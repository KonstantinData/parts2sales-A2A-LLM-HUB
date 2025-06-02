import json
import re
from pathlib import Path
from typing import Any, Dict
from agents.utils.schemas import AgentEvent, PromptQualityResult


class PromptQualityAgent:
    def __init__(
        self,
        openai_client,
        scoring_matrix_name: str = "template",
        agent_name="PromptQualityAgent",
        agent_version="1.0",
        scoring_dir: Path = None,
    ):
        self.openai = openai_client
        self.agent_name = agent_name
        self.agent_version = agent_version

        if scoring_dir is None:
            ROOT = Path(__file__).resolve().parent.parent  # zwei Ebenen hoch
            scoring_dir = ROOT / "config" / "scoring"
        self.scoring_dir = scoring_dir

        self.scoring_matrix_name = scoring_matrix_name
        self.scoring_matrix = self._load_scoring_matrix(scoring_matrix_name)

    def _load_scoring_matrix(self, matrix_name: str) -> Dict[str, Any]:
        py_path = self.scoring_dir / f"{matrix_name}_scoring_matrix.py"
        json_path = self.scoring_dir / f"{matrix_name}_scoring_matrix.json"

        if py_path.exists():
            import importlib.util

            spec = importlib.util.spec_from_file_location("matrix", py_path)
            matrix = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(matrix)
            attr_name = f"{matrix_name.upper()}_SCORING_MATRIX"
            if hasattr(matrix, attr_name):
                return getattr(matrix, attr_name)
            else:
                raise AttributeError(f"Module {py_path} does not contain {attr_name}")
        elif json_path.exists():
            return json.loads(json_path.read_text(encoding="utf-8"))
        else:
            raise FileNotFoundError(
                f"Scoring matrix file not found for '{matrix_name}': {py_path} or {json_path}"
            )

    def run(
        self,
        prompt_text: str,
        base_name: str,
        iteration: int,
        prompt_version: str = None,
        meta: dict = None,
        method: str = "matrix",
    ) -> AgentEvent:
        meta = meta or {}
        score, matrix, feedback, issues = self._score_prompt(prompt_text)
        pass_threshold = score >= 0.9

        result = PromptQualityResult(
            score=score,
            matrix=matrix,
            feedback=feedback,
            pass_threshold=pass_threshold,
            issues=issues,
            prompt_version=prompt_version,
        )

        event = AgentEvent(
            event_type="prompt_quality",
            agent_name=self.agent_name,
            agent_version=self.agent_version,
            step_id=f"{base_name}_iter{iteration}",
            prompt_version=prompt_version,
            meta=meta,
            payload=result.dict(),
        )
        return event

    def _score_prompt(self, prompt_text: str):
        issues = []
        feedback_list = []
        matrix = {}
        prompt = prompt_text.lower()

        checks = {
            "task_clarity": self._check_task_clarity,
            "output_spec": self._check_output_spec,
            "structure_check": self._check_structure,
            "constraint_clarity": self._check_constraint_clarity,
            "reasoning_scope": self._check_reasoning_scope,
            "evalability": self._check_evalability,
            "ambiguity_avoidance": self._check_ambiguity_avoidance,
            "domain_alignment": self._check_domain_alignment,
            "composability": self._check_composability,
            "user_alignment": self._check_user_alignment,
        }

        for dimension, weight in self.scoring_matrix.items():
            check_fn = checks.get(dimension)
            if check_fn is None:
                matrix[dimension] = 0.0
                issues.append(f"Missing check for: {dimension}")
                feedback_list.append(f"{dimension}: No check implemented")
                continue
            result, fb = check_fn(prompt)
            matrix[dimension] = result * weight
            feedback_list.append(f"{dimension}: {fb}")
            if result < 1.0:
                issues.append(fb)

        score = (
            sum(matrix.values()) / sum(self.scoring_matrix.values()) if matrix else 0.0
        )
        feedback = (
            "; ".join(feedback_list) if feedback_list else "No feedback available."
        )
        return score, matrix, feedback, issues

    # Check methods (identisch wie vorher, kannst du bei Bedarf anpassen)
    def _check_task_clarity(self, prompt: str):
        if re.search(r"\b(task|ziel|purpose|describe|instruction)\b", prompt):
            return 1.0, "Task clarity OK"
        return 0.0, "Task not clearly described"

    def _check_output_spec(self, prompt: str):
        if re.search(r"\boutput\b.*\bformat\b|\bformat\b.*\boutput\b", prompt):
            return 1.0, "Output specification OK"
        if "format:" in prompt or "as yaml" in prompt or "as json" in prompt:
            return 1.0, "Output specification OK"
        return 0.0, "Output format not specified"

    def _check_structure(self, prompt: str):
        if "yaml" in prompt or "json" in prompt or "structure:" in prompt:
            return 1.0, "Structure specified"
        return 0.0, "No structural indication found"

    def _check_constraint_clarity(self, prompt: str):
        if "must" in prompt or "do not" in prompt or "rule" in prompt:
            return 1.0, "Constraints present"
        return 0.0, "Constraints/rules missing"

    def _check_reasoning_scope(self, prompt: str):
        if "explain" in prompt or "why" in prompt or "rationale" in prompt:
            return 1.0, "Reasoning required"
        return 0.0, "No reasoning scope indicated"

    def _check_evalability(self, prompt: str):
        if "evaluate" in prompt or "criteria" in prompt or "pass/fail" in prompt:
            return 1.0, "Evalability present"
        return 0.0, "Evalability not defined"

    def _check_ambiguity_avoidance(self, prompt: str):
        if "avoid ambiguity" in prompt or "be specific" in prompt:
            return 1.0, "Ambiguity avoided"
        return 0.0, "Ambiguity avoidance not explicit"

    def _check_domain_alignment(self, prompt: str):
        if "b2b" in prompt or "domain" in prompt or "industry" in prompt:
            return 1.0, "Domain alignment present"
        return 0.0, "Domain not mentioned"

    def _check_composability(self, prompt: str):
        if "extend" in prompt or "modular" in prompt or "reuse" in prompt:
            return 1.0, "Composability addressed"
        return 0.0, "Composability not addressed"

    def _check_user_alignment(self, prompt: str):
        if "user" in prompt or "customer" in prompt or "stakeholder" in prompt:
            return 1.0, "User alignment present"
        return 0.0, "User alignment not explicit"
