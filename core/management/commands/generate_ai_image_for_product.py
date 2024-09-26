from io import BytesIO

import requests
from django.core.files import File
from django.core.management.base import BaseCommand
from PIL import Image

from core.image_utils import generate_food_image
from core.models import Product


class Command(BaseCommand):
    help = "Generate AI images for products without images"

    def handle(self, *args, **options):
        products = Product.objects.filter(image="", ai_generated_image="")

        for product in products:
            self.stdout.write(f"Generating image for product: {product.name}")

            # Generate the AI image
            image_url = generate_food_image(product.name)

            if image_url:
                # Download the image
                response = requests.get(image_url)
                if response.status_code == 200:
                    img = Image.open(BytesIO(response.content))

                    # Save the original AI generated image
                    img_io = BytesIO()
                    img.save(img_io, format="JPEG", quality=95)
                    file_name = f"{product.slug}_ai.jpg"
                    product.ai_generated_image.save(file_name, File(img_io), save=True)

                    # Create and save the compressed version
                    compressed_img_io = BytesIO()
                    img.save(compressed_img_io, format="JPEG", quality=60, optimize=True)
                    compressed_file_name = f"{product.slug}_ai_compressed.jpg"
                    product.compressed_ai_generated_image.save(compressed_file_name, File(compressed_img_io), save=True)

                    self.stdout.write(self.style.SUCCESS(f"Successfully generated and saved images for {product.name}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Failed to download image for {product.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Failed to generate image for {product.name}"))

        self.stdout.write(self.style.SUCCESS("Finished generating images for products"))
