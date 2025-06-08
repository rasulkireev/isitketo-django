from django.contrib import sitemaps
from django.contrib.sitemaps import GenericSitemap
from django.urls import reverse

from core.models import BlogPost, Product


class StaticViewSitemap(sitemaps.Sitemap):
    """Generate Sitemap for the site"""

    priority = 0.9
    protocol = "https"

    def items(self):
        """Identify items that will be in the Sitemap

        Returns:
            List: urlNames that will be in the Sitemap
        """
        return [
            "home",
            "products",
            "product_categories",
            "blog_posts",
        ]

    def location(self, item):
        """Get location for each item in the Sitemap

        Args:
            item (str): Item from the items function

        Returns:
            str: Url for the sitemap item
        """
        return reverse(item)


class ProductCategoriesSitemap(sitemaps.Sitemap):
    priority = 0.8
    protocol = "https"
    changefreq = "daily"

    def items(self):
        return Product.objects.values_list("category", flat=True).distinct().order_by("category")

    def location(self, item):
        return reverse("product_category_list", kwargs={"category": item})


sitemaps = {
    "static": StaticViewSitemap,
    "blog": GenericSitemap(
        {"queryset": BlogPost.objects.all(), "date_field": "created_at"},
        priority=0.95,
        protocol="https",
    ),
    "products": GenericSitemap(
        {
            "queryset": Product.objects.all(),
            "date_field": "created_at",
        },
        priority=0.9,
        protocol="https",
    ),
    "product_categories": ProductCategoriesSitemap,
}
