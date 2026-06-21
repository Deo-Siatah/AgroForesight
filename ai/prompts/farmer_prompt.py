from pathlib import Path
import yaml

class FarmerPrompt:

    def __init__(self):
        prompt_path = (
            Path(__file__)
            .parent
            / "farmer_prompt.yaml"
        )

        with open(
            prompt_path,
            "r",
            encoding="utf-8",
        ) as file:
            self.config = yaml.safe_load(file)

    def build_prompt(
        self,
        recommendation_data: dict,
    ) -> str:

        role = self.config["role"]
        objective = self.config["objective"]

        language = self.config["language"]
        tone = self.config["tone"]
        verbosity = self.config["verbosity"]

        return f"""
{role}

OBJECTIVE:
{objective}

LANGUAGE:
{language}

TONE:
{tone}

VERBOSITY:
{verbosity}

RULE-BASED RECOMMENDATION:

{recommendation_data}

Generate a response following the configured rules.

Return only:
1. title
2. message
"""