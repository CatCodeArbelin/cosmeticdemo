import json
import re
from pathlib import Path
from openai import OpenAI


SYSTEM_PROMPT = """Ты AI-помощник менеджера магазина профессиональной косметики.
Ты НЕ отвечаешь клиенту напрямую.
Ты предлагаешь менеджеру 2 коротких варианта ответа.
Ответы должны быть на русском языке.
Обращение на “вы”.
Стиль: профессиональный, дружелюбный, без давления.
Не давай медицинских обещаний.
Не используй слова “лечит”, “избавит от заболевания”, “гарантирует результат”.
Если клиент спрашивает про заболевания кожи, посоветуй обратиться к врачу/дерматологу и предложи только общий уход.
Всегда старайся задать 1–2 уточняющих вопроса, если данных недостаточно."""


class AIService:
    def __init__(self, api_key: str, model: str):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.knowledge_base = Path("app/knowledge_base.md").read_text(encoding="utf-8")

    def _fallback_variants(self):
        return (
            "Спасибо за обращение! Подскажите, пожалуйста, ваш текущий уход и ориентир по бюджету, чтобы я предложил(а) подходящие варианты для вашего типа кожи.",
            "С радостью помогу с подбором. Уточните, пожалуйста, есть ли чувствительность к активам (кислоты, ретинол, витамин C) и какие средства вы используете сейчас?",
        )

    def _parse_json_fallback(self, raw: str):
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return None
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None

    def generate_variants(self, source: str, client_name: str, client_message: str):
        user_prompt = f"""Источник: {source}
Имя клиента: {client_name}
Сообщение клиента: {client_message}

База знаний:
{self.knowledge_base}

Верни строго JSON формата:
{{
  \"variant_1\": \"...\",
  \"variant_2\": \"...\"
}}"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.5,
            )
            content = response.choices[0].message.content or ""
            parsed = None
            try:
                parsed = json.loads(content)
            except json.JSONDecodeError:
                parsed = self._parse_json_fallback(content)

            if not parsed or "variant_1" not in parsed or "variant_2" not in parsed:
                return self._fallback_variants()

            return parsed["variant_1"].strip(), parsed["variant_2"].strip()
        except Exception:
            return self._fallback_variants()
