from django.conf import settings
from django_q.tasks import async_task

from integrations.fatsecret import FatSecretClient
from isitketo.utils import get_isitketo_logger

logger = get_isitketo_logger(__name__)

fatsecret = FatSecretClient(client_id=settings.FAT_SECRET_CLIENT_ID, client_secret=settings.FAT_SECRET_CLIENT_SECRET)


def schedule_products_creation(product_name: str):
    logger.info("Scheduling Products Creation", product_name=product_name)

    results = fatsecret.search(product_name)
    count = 0
    for result in results:
        food_id = result.get("food_id", "")
        async_task(create_product, food_id)
        count += 1

    return f"Scheduled {count} products to get created."


def create_product(food_id):
    fatsecret.get_product_info(food_id)
