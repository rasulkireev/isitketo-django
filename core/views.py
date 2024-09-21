from django.db.models import Case, IntegerField, Prefetch, Q, Value, When
from django.http import JsonResponse
from django.views.generic import DetailView, ListView, TemplateView

from core.models import Product, Tag
from isitketo.utils import get_isitketo_logger

logger = get_isitketo_logger(__name__)


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        perfect_keto_foods = Product.objects.filter(rating=5)[:4]

        context["perfect_keto_foods"] = [
            {
                "image_url": product.image.url,
                "keto_meter_image": f"vendors/images/keto-meter-{product.rating}.png",
                "name": product.name,
                "slug": product.slug,
            }
            for product in perfect_keto_foods
        ]

        return context


class ProductsView(ListView):
    model = Product
    template_name = "pages/products.html"
    context_object_name = "products"
    paginate_by = 20
    ordering = "-created_at"


class ProductCategoryListView(ListView):
    model = Product
    template_name = "pages/product_category_list.html"
    context_object_name = "products"
    paginate_by = 20
    ordering = "-created_at"

    def get_queryset(self):
        self.category = self.kwargs["category"]
        return Product.objects.filter(category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context


class ProductCategories(ListView):
    template_name = "pages/product_categories.html"
    context_object_name = "categories"

    def get_queryset(self):
        unique_categories = Product.objects.values_list("category", flat=True).distinct().order_by("category")

        queryset = []
        for category in unique_categories:
            products = Product.objects.filter(category=category).prefetch_related(
                Prefetch("tags", queryset=Tag.objects.all())
            )[:4]

            queryset.append({"category": category, "products": products})

        return queryset


class ProductView(DetailView):
    model = Product
    template_name = "products/product_details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["keto_meter_image_path"] = f"vendors/images/keto-meter-{self.object.rating}.png"

        related_products = (
            Product.objects.filter((Q(category=self.object.category) | Q(rating=self.object.rating)) & Q(rating__gte=4))
            .exclude(id=self.object.id)
            .distinct()[:4]
        )

        context["related_keto_foods"] = [
            {
                "image_url": product.image.url,
                "keto_meter_image": f"vendors/images/keto-meter-{product.rating}.png",
                "name": product.name,
                "slug": product.slug,
            }
            for product in related_products
        ]

        return context


def search_products(request):
    query = request.GET.get("query", "")
    if len(query) > 2:
        logger.info("User Search Initiated", query=query)
        products = (
            Product.objects.annotate(
                name_match=Case(
                    When(name__icontains=query, then=Value(3)), default=Value(0), output_field=IntegerField()
                ),
                short_desc_match=Case(
                    When(short_description__icontains=query, then=Value(2)),
                    default=Value(0),
                    output_field=IntegerField(),
                ),
                full_desc_match=Case(
                    When(full_description__icontains=query, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                ),
            )
            .filter(
                Q(name__icontains=query) | Q(short_description__icontains=query) | Q(full_description__icontains=query)
            )
            .order_by("-name_match", "-short_desc_match", "-full_desc_match", "name")[:10]
        )

        data = list(products.values("name", "slug", "image"))

        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)
