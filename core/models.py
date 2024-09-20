from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import JSONField

from core.base_models import BaseModel
from core.choices import FoodCategory


class Product(BaseModel):
    name = models.CharField(max_length=250, blank=True)
    slug = models.SlugField(max_length=150, unique=True)
    category = models.CharField(
        max_length=40,
        default=FoodCategory.OTHER.value,
        choices=[(category.value, category.value) for category in FoodCategory],
    )
    tags = models.ManyToManyField("Tag", through="ProductTag", related_name="product", blank=True)
    data = JSONField(default=dict)
    has_plural_title = models.BooleanField(default=False)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True)
    ai_generated_image = models.ImageField(upload_to="ai_product_image/", blank=True)
    image = models.ImageField(upload_to="product_image/", blank=True)

    short_description = models.CharField(max_length=250)
    full_description = models.TextField()

    property

    def keto_meter_image_path(self):
        return f"/static/vendors/images/keto-meter-{self.rating}.png"


class Tag(BaseModel):
    name = models.CharField(max_length=250, blank=True)


class ProductTag(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
