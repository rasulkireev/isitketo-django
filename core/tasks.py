import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.temp import NamedTemporaryFile
from django.utils.text import slugify
from django_q.tasks import async_task

from core.image_utils import compress_image, generate_food_image
from core.models import Product, ProductTag, Tag
from core.utils import (
    generate_tags_for_food,
    get_detailed_keto_description,
    guess_food_category,
    is_food_keto_friendly_short_answer,
    is_food_name_plural,
    rate_food_for_keto,
)
from integrations.fatsecret import FatSecretClient
from isitketo.utils import get_isitketo_logger

logger = get_isitketo_logger(__name__)

fatsecret_client = FatSecretClient(
    client_id=settings.FAT_SECRET_CLIENT_ID, client_secret=settings.FAT_SECRET_CLIENT_SECRET
)


def schedule_products_creation(product_name: str):
    logger.info("Scheduling Products Creation", product_name=product_name)

    results = fatsecret_client.search(product_name)
    count = 0
    for result in results:
        food_id = result.get("food_id", "")
        async_task(create_product, food_id)
        count += 1

    return f"Scheduled {count} products to get created for '{product_name}' query."


def create_product(food_id):
    logger.info("Creating Product", food_id=food_id)
    product_info = fatsecret_client.get_product_info(food_id)

    macros = product_info["servings"]["serving"][0]
    product_name = product_info.get("food_name")

    product_brand = product_info.get("brand_name", "")
    if product_brand != "":
        product_name = product_name + f" by {product_brand}"

    slug = slugify(product_name)
    category = guess_food_category(product_name)
    has_plural_title = is_food_name_plural(product_name)
    rating = rate_food_for_keto(product_name, macros)
    short_description = is_food_keto_friendly_short_answer(product_name)
    full_description = get_detailed_keto_description(product_name, macros)

    product = Product.objects.create(
        name=product_name,
        slug=slug,
        category=category.value,
        has_plural_title=has_plural_title,
        rating=rating,
        short_description=short_description,
        full_description=full_description,
        data=product_info,
    )

    image_url = product_info["food_images"]["food_image"][0]["image_url"]
    response = requests.get(image_url)
    if response.status_code == 200:
        product.image.save(f"{slug}.jpg", ContentFile(response.content), save=True)

        compressed_image = compress_image(product.image)
        product.compressed_image.save(f"{slug}_compressed.jpg", compressed_image, save=False)

    tags = generate_tags_for_food(product_name)
    for tag_name in tags:
        tag, _ = Tag.objects.get_or_create(name=tag_name)
        ProductTag.objects.create(product=product, tag=tag)

    async_task(generate_and_save_ai_image, product.id)

    return f"Created Product Object: {product.name}"


def generate_and_save_ai_image(product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        logger.warning(f"Product with id {product_id} does not exist.")
        return

    logger.info("Generating AI Image for Product", product_name=product.name)

    image_url = generate_food_image(product.name)

    if not image_url:
        logger.warning(f"Failed to generate AI image for product: {product.name}")
        return

    # Download the image
    response = requests.get(image_url)
    if response.status_code != 200:
        logger.warning(f"Failed to download AI image for product: {product.name}")
        return

    # Save original AI image
    original_image = ContentFile(response.content)
    product.ai_generated_image.save(f"{product.slug}_ai.webp", original_image, save=False)

    # Compress and save the AI image
    with NamedTemporaryFile() as temp_file:
        temp_file.write(response.content)
        temp_file.flush()

        product.ai_generated_image.save(f"{product.slug}_ai.webp", temp_file, save=False)
        compressed_image = compress_image(product.ai_generated_image)
        product.compressed_ai_generated_image.save(f"{product.slug}_ai_compressed.jpg", compressed_image, save=False)

    product.save()

    return f"AI image generated and saved for product: {product.name}"
