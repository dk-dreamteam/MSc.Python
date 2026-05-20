import json
import os
from groq import Groq


class AIService:
    def __init__(self):
        api_key = os.environ.get('GROQ_API_KEY', '')
        self.client = Groq(api_key=api_key) if api_key else None
        self.model = os.environ.get('GROQ_MODEL', 'mixtral-8x7b-32768')

    def analyze_ticket(self, title, description):
        if not self.client:
            return {'priority': 'Medium', 'confidence': 0.5}
        prompt = (
            f"Analyze this city problem report and suggest:\n"
            f"1. Priority (High/Medium/Low)\n"
            f"2. Category confidence (0.00-1.00)\n\n"
            f"Title: {title}\n"
            f"Description: {description}\n\n"
            f"Respond with JSON only: {{\"priority\": \"...\", \"confidence\": 0.00}}"
        )

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=100
            )
            response = completion.choices[0].message.content.strip()
            result = json.loads(response)
            return {
                'priority': result.get('priority', 'Medium'),
                'confidence': float(result.get('confidence', 0.5))
            }
        except Exception:
            return {'priority': 'Medium', 'confidence': 0.5}
