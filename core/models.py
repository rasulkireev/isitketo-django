from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import JSONField
from django.urls import reverse

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
    compressed_ai_generated_image = models.ImageField(upload_to="compressed_ai_product_image/", blank=True)
    image = models.ImageField(upload_to="product_image/", blank=True)
    compressed_image = models.ImageField(upload_to="compressed_product_image/", blank=True)

    short_description = models.CharField(max_length=350)
    full_description = models.TextField()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("product", kwargs={"slug": self.slug})

    @property
    def keto_meter_image_path(self):
        return f"/static/vendors/images/keto-meter-{self.rating}.png"


class Tag(BaseModel):
    name = models.CharField(max_length=250, blank=True)


class ProductTag(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)


class BlogPost(BaseModel):
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=250)
    tags = models.TextField()
    content = models.TextField()
    icon = models.ImageField(upload_to="blog_post_icons/", blank=True)
    image = models.ImageField(upload_to="blog_post_images/", blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog_post", kwargs={"slug": self.slug})


class GeneratedKeywords(BaseModel):
    keyword = models.CharField(max_length=250, unique=True)

    def __str__(self):
        return self.keyword
