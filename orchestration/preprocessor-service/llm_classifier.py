import os
import logging
from groq import Groq
from data.repository import TicketRepository

repo = TicketRepository()

logger = logging.getLogger(__name__)


class LLMClassifierService:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        model = os.getenv("GROQ_MODEL")
        if not api_key or not model:
            raise ValueError("GROQ_API_KEY and GROQ_MODEL must be set")

        self.client = Groq(api_key=api_key)
        self.model = model

    def _getCategories(self) -> list[dict]:
        return repo.get_categories()

    def Classify(self, text: str) -> int:
        categories = self._getCategories()
        categories_prompt_string = ", ".join(f'{cat["id"]}: {cat["name"]}' for cat in categories)
        prompt = (
            f"Classify the following text into one of these categories: {categories_prompt_string}. "
            "Return only the category ID as a single number, nothing else.\n\n"
            f"Text: {text}"
        )
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        category_id = int(response.choices[0].message.content.strip())
        logger.info("Classified text into category: %d", category_id)
        return category_id

    def ClassifyPriority(self, text: str) -> str:
        prompt = (
            "Classify the following text based on priority. "
            "Return only one word or phrase from these options: "
            "'⚠️ Επείγον' or 'Κανονική Προτεραιότητα'. "
            "Anything that is not hygiene-threatening is 'Κανονική Προτεραιότητα'.\n\n"
            f"Text: {text}"
        )
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        priority = response.choices[0].message.content.strip()
        logger.info("Classified text priority: %s", priority)
        return priority
