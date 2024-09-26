from typing import Dict, List

import anthropic
from django.conf import settings
from django.forms.utils import ErrorList

from core.choices import FoodCategory
from isitketo.utils import get_isitketo_logger

logger = get_isitketo_logger(__name__)

anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


class DivErrorList(ErrorList):
    def __str__(self):
        return self.as_divs()

    def as_divs(self):
        if not self:
            return ""
        return f"""
            <div class="p-4 my-4 bg-red-50 rounded-md border border-red-600 border-solid">
              <div class="flex">
                <div class="flex-shrink-0">
                  <!-- Heroicon name: solid/x-circle -->
                  <svg class="w-5 h-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"> # noqa: E501
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" /> # noqa: E501
                  </svg>
                </div>
                <div class="ml-3 text-sm text-red-700">
                      {''.join([f'<p>{e}</p>' for e in self])}
                </div>
              </div>
            </div>
         """


def guess_food_category(food_name):
    logger.info("Generating Food Category", food_name=food_name)
    prompt = f"""Given the following food categories:

{', '.join(FoodCategory)}

Please categorize the food item "{food_name}" into one of these categories. Respond with only the category name, nothing else."""

    message = anthropic_client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        temperature=0,
        system="You are a world-class Nutritionist.",
        messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
    )

    guessed_category = message.content[0].text.strip()

    try:
        return FoodCategory(guessed_category)
    except ValueError:
        return FoodCategory.OTHER


def generate_tags_for_food(food_name: str) -> List[str]:
    logger.info("Generating Tags for Product", food_name=food_name)
    prompt = f"""Given the food item "{food_name}", please generate a list of relevant tags.
    These tags should describe characteristics such as:
    - Flavor profile
    - Texture
    - Cooking method
    - Dietary considerations (e.g., vegan, gluten-free)
    - Cultural associations
    - Common uses or pairings

    Provide the tags as a comma-separated list, with no additional text or explanation.
    Limit the response to 10 tags maximum."""

    message = anthropic_client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        temperature=0.2,
        system="You are a culinary expert with extensive knowledge of food characteristics and classifications.",
        messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
    )

    tags = [tag.strip() for tag in message.content[0].text.split(",")]

    return tags


def is_food_name_plural(food_name: str) -> bool:
    prompt = f"""Determine if the food item name "{food_name}" is typically used in its plural form.
    Consider the following:
    - Is this food item usually referred to in plural (e.g., "grapes", "beans")?
    - Is it a mass noun that doesn't have a typical plural form (e.g., "rice", "milk")?
    - Is it typically singular (e.g., "apple", "carrot")?

    Respond with only "True" if it's typically plural, or "False" if it's typically singular or a mass noun. Provide no other text."""

    message = anthropic_client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        temperature=0,
        system="You are a linguistic expert specializing in food terminology.",
        messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
    )

    response = message.content[0].text.strip().lower()
    is_plural = response == "true"

    return is_plural


def rate_food_for_keto(food_name: str, macros: Dict[str, str]) -> int:
    logger.info("Generating a Keto Rating for Product", food_name=food_name)

    serving_description = macros.get("serving_description", "serving")
    metric_serving_amount = macros.get("metric_serving_amount", "")
    metric_serving_unit = macros.get("metric_serving_unit", "")

    serving_info = f"{serving_description}"
    if metric_serving_amount and metric_serving_unit:
        serving_info += f" ({metric_serving_amount} {metric_serving_unit})"

    prompt = f"""Given the food item "{food_name}" and its nutritional information, rate its suitability for a ketogenic diet on a scale of 1 to 5, where 1 is least suitable and 5 is most suitable.

Nutritional information per {serving_info}:
- Calories: {macros.get('calories', 'N/A')}
- Carbohydrates: {macros.get('carbohydrate', 'N/A')}g
- Protein: {macros.get('protein', 'N/A')}g
- Fat: {macros.get('fat', 'N/A')}g
- Fiber: {macros.get('fiber', 'N/A')}g

Consider the following factors:
1. Low carbohydrate content (the lower, the better for keto)
2. High fat content (the higher, the better for keto)
3. Moderate protein content
4. Net carbs (total carbs minus fiber)
5. Overall suitability for maintaining ketosis

Provide only a single number (1, 2, 3, 4, or 5) as your response, with no additional explanation."""

    message = anthropic_client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        temperature=0,
        system="You are a nutritionist specializing in ketogenic diets.",
        messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
    )

    try:
        rating = int(message.content[0].text.strip())
        if 1 <= rating <= 5:
            return rating
        else:
            return 1
    except ValueError:
        return 1


def is_food_keto_friendly_short_answer(food_name: str) -> str:
    logger.info("Generating a Short Answer for Product", food_name=food_name)
    prompt = f"""Is {food_name} keto friendly?
    Provide a concise answer explaining why or why not.
    Your response should be informative yet brief, not exceeding 250 characters."""

    message = anthropic_client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        temperature=0.2,
        system="You are a nutritionist specializing in ketogenic diets. Provide concise, accurate information about food items' compatibility with a keto diet.",
        messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
    )

    return message.content[0].text.strip()


def get_detailed_keto_description(food_name: str, macros: Dict[str, str]) -> str:
    logger.info("Generating a Detailed Answer for Product", food_name=food_name)

    serving_description = macros.get("serving_description", "serving")
    metric_serving_amount = macros.get("metric_serving_amount", "")
    metric_serving_unit = macros.get("metric_serving_unit", "")

    serving_info = f"{serving_description}"
    if metric_serving_amount and metric_serving_unit:
        serving_info += f" ({metric_serving_amount} {metric_serving_unit})"

    nutritional_info = f"""
    - Calories: {macros.get('calories', 'N/A')}
    - Carbohydrates: {macros.get('carbohydrate', 'N/A')}g
    - Fiber: {macros.get('fiber', 'N/A')}g
    - Protein: {macros.get('protein', 'N/A')}g
    - Fat: {macros.get('fat', 'N/A')}g"""

    if "saturated_fat" in macros:
        nutritional_info += f"\n    - Saturated Fat: {macros['saturated_fat']}g"
    if "polyunsaturated_fat" in macros:
        nutritional_info += f"\n    - Polyunsaturated Fat: {macros['polyunsaturated_fat']}g"
    if "monounsaturated_fat" in macros:
        nutritional_info += f"\n    - Monounsaturated Fat: {macros['monounsaturated_fat']}g"

    prompt = f"""Provide a detailed description of {food_name} and its relevance to the ketogenic diet. Use the following nutritional information for a {serving_info}:
    {nutritional_info}

    Include the following points in your analysis:

    1. Brief overview of the food item
    2. Detailed macronutrient profile analysis based on the provided data
    3. Net carbs calculation and its significance for keto
    4. How well this food fits into a ketogenic diet
    5. Potential benefits for keto dieters
    6. Potential drawbacks or considerations for keto dieters
    7. Suggested serving size or how it might fit into a keto meal plan
    8. Any micronutrients or other health benefits worth mentioning

    Your response should be comprehensive yet concise, aiming for about 200-250 words."""

    logger.info(f"Generating detailed keto description for: {food_name}")

    message = anthropic_client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=2000,
        temperature=0.2,
        system="You are a nutritionist and keto diet expert. Provide accurate, detailed information about food items and their compatibility with a ketogenic diet, based on the provided nutritional data.",
        messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
    )

    response = message.content[0].text.strip()

    logger.info(f"Generated detailed keto description for {food_name}")

    return response
