"""
Use Case Detection Agent:
- Ermittelt Anwendungsfälle für einen Artikel basierend auf Features und Prompt.
"""

class UseCaseDetectionAgent:
    def __init__(self, prompt_template_path="prompts/00-templates/usecase_detect_v1.yaml"):
        self.prompt_template_path = prompt_template_path

    def detect_usecases(self, features, article):
        # TODO: Prompt bauen, LLM aufrufen, Use Cases extrahieren
        raise NotImplementedError("Use Case Detection hier implementieren.")
