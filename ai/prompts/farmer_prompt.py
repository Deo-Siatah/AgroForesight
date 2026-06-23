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
        recommendation: dict,
        weather:dict,
        crop_type: str | None = None,
        county: str | None = None,
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

CROP TYPE:
{crop_type or "N/A"}

COUNTY:
{county or "N/A"}

WEATHER DATA:

{weather or "N/A"}

RULE-BASED RECOMMENDATION:

{recommendation}

Generate a response following the configured rules.

Return only:
1. title
2. message
"""