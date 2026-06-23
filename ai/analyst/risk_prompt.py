from pathlib import Path
import yaml


class RiskPrompt:

    def __init__(self):
        prompt_path = Path(__file__).parent / "risk_prompt.yaml"

        with open(prompt_path, "r", encoding="utf-8") as file:
            self.config = yaml.safe_load(file)

    def build_prompt(self, risk_data: dict) -> str:
        role = self.config.get("role", "")
        objective = self.config.get("objective", "")
        tone = self.config.get("tone", "")
        language = self.config.get("language", "")
        output_format = self.config.get("output_format", "")
        json_schema = self.config.get("json_schema", {})

        constraints = self.config.get("constraints", [])
        instructions = self.config.get("instructions", [])

        constraints_text = "\n".join(f"- {c}" for c in constraints)
        instructions_text = "\n".join(f"- {i}" for i in instructions)
        
        # Build JSON schema description
        schema_text = "\n".join(
            f"- {key}: {value}" for key, value in json_schema.items()
        )

        return f"""
{role}

OBJECTIVE:
{objective}

LANGUAGE:
{language}

TONE:
{tone}

CONSTRAINTS:
{constraints_text}

INSTRUCTIONS:
{instructions_text}

RISK DATA:
{risk_data}

OUTPUT FORMAT:
{output_format}

JSON SCHEMA:
{schema_text}

Return ONLY valid JSON. No markdown, no extra text.
"""