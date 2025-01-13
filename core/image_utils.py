import os
import random
from io import BytesIO

import replicate
from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image

from isitketo.utils import get_isitketo_logger

logger = get_isitketo_logger(__name__)

os.environ["REPLICATE_API_TOKEN"] = settings.REPLICATE_API_KEY


def generate_food_image(food_item, style="realistic", size="medium"):
    """
    Generate a realistic image of a food item using Replicate API and Flux Pro model.

    :param food_item: The name of the food item to generate
    :param style: The style of the image (default is "realistic")
    :param size: The size of the food item (default is "medium")
    :return: URL of the generated image
    """
    logger.info("Generating the AI image", food_name=food_item)

    # List of adjectives to enhance the prompt
    adjectives = ["delicious", "mouth-watering", "appetizing", "tempting", "scrumptious"]

    # List of photography styles to enhance realism
    photo_styles = ["food photography", "studio lighting", "high-resolution", "4K", "detailed"]

    # Randomly select an adjective and a photo style
    adj = random.choice(adjectives)
    photo_style = random.choice(photo_styles)

    # Construct the prompt
    prompt = f"A {adj} {size} {food_item}, {style} style, {photo_style}, centered composition"

    # Set up the input for the Replicate API
    input_data = {
        "prompt": prompt,
        "negative_prompt": "cartoon, illustration, low quality, blurry, text, watermark",
    }

    try:
        # Run the model
        output = replicate.run("black-forest-labs/flux-1.1-pro", input=input_data)

        # The output is expected to be a URL to the generated image
        return output
    except Exception as e:
        logger.warning(f"An error occurred: {e}")
        return None


def compress_image(image_field, quality=20, format="JPEG"):
    """
    Compress the given image field and return a ContentFile of the compressed image.

    :param image_field: ImageField instance
    :param quality: int, compression quality (1-95)
    :param format: str, output format ('JPEG', 'PNG', etc.)
    :return: ContentFile of the compressed image
    """
    logger.info("Compressing the image", image=image_field)

    img = Image.open(image_field)

    # Convert to RGB if image has an alpha channel
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])  # 3 is the alpha channel
        img = bg

    output = BytesIO()
    img.save(output, format=format, quality=quality, optimize=True)
    output.seek(0)

    return ContentFile(output.read())
