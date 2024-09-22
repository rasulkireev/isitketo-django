import io
import os

import yaml
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from PIL import Image

from core.choices import FoodCategory
from core.models import Product, ProductTag, Tag
from isitketo.utils import get_isitketo_logger

logger = get_isitketo_logger(__name__)


class Command(BaseCommand):
    help = "Import food data from Markdown files"

    def compress_image(self, image_path, quality=5):
        with Image.open(image_path) as img:
            img_io = io.BytesIO()
            img.save(img_io, format="JPEG", quality=quality)
            img_io.seek(0)
            return ContentFile(img_io.getvalue())

    def handle(self, *args, **options):
        foods_dir = os.path.join(settings.BASE_DIR, "core", "old_content", "foods")
        images_dir = os.path.join(settings.BASE_DIR, "core", "old_content", "food-images")

        for filename in os.listdir(foods_dir):
            if filename.endswith(".md"):
                with open(os.path.join(foods_dir, filename), "r") as file:
                    content = file.read()

                # Split the content into frontmatter and markdown
                _, frontmatter, markdown = content.split("---", 2)

                # Parse the frontmatter
                data = yaml.safe_load(frontmatter)

                # Create or update the Product
                product, created = Product.objects.update_or_create(
                    name=data["name"],
                    defaults={
                        "category": data.get("category", FoodCategory.OTHER.value),
                        "slug": slugify(data["name"]),
                        "short_description": data.get("short_answer", ""),
                        "full_description": markdown.strip(),
                        "has_plural_title": data.get("has_plural_title", False),
                        "rating": data.get("rating"),
                        "data": {
                            "usda_info": data.get("usda_info", {}),
                            "affiliate_links": data.get("affiliate_links", []),
                            "usda_multiplier": data.get("usda_multiplier"),
                            "serving_size_formatted": data.get("serving_size_formatted"),
                            "creation_time": data.get("creation_time"),
                            "last_modified_time": data.get("last_modified_time"),
                            "has_affiliate_links": data.get("has_affiliate_links", False),
                        },
                    },
                )

                image_filename = data.get("image", "").split("/")[-1]
                image_path = os.path.join(images_dir, image_filename)
                if os.path.exists(image_path):
                    try:
                        # Save original image
                        with open(image_path, "rb") as img_file:
                            file_content = ContentFile(img_file.read(), name=image_filename)
                            product.image.save(f"{image_filename}", file_content, save=False)

                        # Save compressed image
                        compressed_content = self.compress_image(image_path)
                        compressed_filename = f"compressed_{image_filename}"
                        product.compressed_image.save(compressed_filename, compressed_content, save=False)

                        product.save()
                    except Exception as e:
                        logger.error(f"Error uploading image for {data['name']}: {str(e)}")
                        self.stdout.write(self.style.ERROR(f'Failed to upload image for {data["name"]}: {str(e)}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Image not found for {data["name"]}'))

                # Add tags
                tags = data.get("tags", [])
                if "category" in data:
                    tags.append(data["category"])

                for tag_name in tags:
                    tag, _ = Tag.objects.get_or_create(name=tag_name)
                    ProductTag.objects.get_or_create(product=product, tag=tag)

                self.stdout.write(self.style.SUCCESS(f'Successfully imported {data["name"]}'))
