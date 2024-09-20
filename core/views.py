from random import sample
from django.views.generic import TemplateView, ListView, DetailView
from django.db.models import Q, Prefetch

from isitketo.utils import get_isitketo_logger

from core.models import Product, Tag
from core.choices import FoodCategory

logger = get_isitketo_logger(__name__)

class HomeView(TemplateView):
    template_name = "pages/home.html"


class ProductsView(ListView):
    model = Product
    template_name = "pages/products.html"
    context_object_name = "products"
    paginate_by = 20
    ordering = "-created_at"


class ProductCategoryListView(ListView):
    model = Product
    template_name = 'pages/product_category_list.html'
    context_object_name = 'products'
    paginate_by = 20
    ordering = "-created_at"

    def get_queryset(self):
        self.category = self.kwargs['category']
        return Product.objects.filter(category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class ProductCategories(ListView):
    template_name = 'pages/product_categories.html'
    context_object_name = 'categories'

    def get_queryset(self):
        unique_categories = Product.objects.values_list('category', flat=True).distinct().order_by('category')

        queryset = []
        for category in unique_categories:
            products = Product.objects.filter(category=category).prefetch_related(
                Prefetch('tags', queryset=Tag.objects.all())
            )[:4]

            queryset.append({
                'category': category,
                'products': products
            })

        return queryset


class ProductView(DetailView):
    model = Product
    template_name = "products/product_details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["keto_meter_image_path"] = f"vendors/images/keto-meter-{self.object.rating}.png"

        related_products = Product.objects.filter(
            (Q(category=self.object.category) | Q(rating=self.object.rating)) &
            Q(rating__gte=4)
        ).exclude(id=self.object.id).distinct()[:4]

        context["related_keto_foods"] = [
            {
                'image_url': product.image.url,
                'keto_meter_image': f"vendors/images/keto-meter-{product.rating}.png",
                'name': product.name,
                'slug': product.slug,
            }
            for product in related_products
        ]

        return context
