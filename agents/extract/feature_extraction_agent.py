"""
Feature Extraction Agent:
- Extrahiert Features aus Artikeldaten mithilfe eines Prompt-Templates und OpenAI API.
- Prompt-Template wird aus der Config geladen und mit Artikel-Infos gefüllt.
"""

class FeatureExtractionAgent:
    def __init__(self, prompt_template_path="prompts/00-templates/feature_setup_v1.yaml"):
        self.prompt_template_path = prompt_template_path

    def load_template(self):
        with open(self.prompt_template_path, encoding="utf-8") as f:
            return f.read()

    def build_prompt(self, article):
        template = self.load_template()
        return template.format(**article)

    def extract_features(self, article):
        prompt = self.build_prompt(article)
        # Call OpenAI API hier
        raise NotImplementedError("OpenAI API Call hier implementieren.")
