import random

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Case, Count, IntegerField, Prefetch, Q, Value, When
from django.db.models.functions import Lower
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.views.generic import DetailView, ListView, TemplateView
from django_q.tasks import async_task

from core.models import Product, Tag
from core.tasks import schedule_products_creation
from isitketo.utils import get_isitketo_logger

logger = get_isitketo_logger(__name__)


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        count = Product.objects.filter(rating=5).aggregate(count=Count("id"))["count"]
        random_indices = random.sample(range(count), min(4, count))
        perfect_keto_foods = [Product.objects.filter(rating=5)[index] for index in random_indices]

        context["other_keto_foods"] = []
        for product in perfect_keto_foods:
            image_url = None
            if product.compressed_ai_generated_image:
                image_url = product.compressed_ai_generated_image.url
            elif product.compressed_image:
                image_url = product.compressed_image.url

            if image_url:
                context["other_keto_foods"].append(
                    {
                        "image_url": image_url,
                        "keto_meter_image": f"vendors/images/keto-meter-{product.rating}.png",
                        "name": product.name,
                        "slug": product.slug,
                    }
                )

        return context


class ProductsView(ListView):
    model = Product
    template_name = "pages/products.html"
    context_object_name = "products"
    paginate_by = 8
    ordering = "-created_at"


class ProductCategoryListView(ListView):
    model = Product
    template_name = "pages/product_category_list.html"
    context_object_name = "products"
    paginate_by = 8
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
        # Get unique categories, converting to lowercase and ordering
        unique_categories = (
            Product.objects.annotate(category_lower=Lower("category"))
            .values_list("category_lower", flat=True)
            .distinct()
            .order_by("category_lower")
        )

        queryset = []
        for category_lower in unique_categories:
            # Get the original category name (preserving the original case for display)
            original_category = (
                Product.objects.filter(category__iexact=category_lower).values_list("category", flat=True).first()
            )

            products = Product.objects.filter(category__iexact=category_lower).prefetch_related(
                Prefetch("tags", queryset=Tag.objects.all())
            )[:4]

            queryset.append({"category": original_category, "products": products})

        return queryset


class ProductView(DetailView):
    model = Product
    template_name = "products/product_details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["keto_meter_image_path"] = f"vendors/images/keto-meter-{self.object.rating}.png"

        count = Product.objects.filter(rating=5).exclude(id=self.object.id).aggregate(count=Count("id"))["count"]
        random_indices = random.sample(range(count), min(4, count))
        perfect_keto_foods = [Product.objects.filter(rating=5)[index] for index in random_indices]

        context["other_keto_foods"] = []
        for product in perfect_keto_foods:
            image_url = None
            if product.compressed_ai_generated_image:
                image_url = product.compressed_ai_generated_image.url
            elif product.compressed_image:
                image_url = product.compressed_image.url

            if image_url:
                context["other_keto_foods"].append(
                    {
                        "image_url": image_url,
                        "keto_meter_image": f"vendors/images/keto-meter-{product.rating}.png",
                        "name": product.name,
                        "slug": product.slug,
                    }
                )

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

        data = list(products.values("name", "slug"))

        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)


@user_passes_test(lambda u: u.is_superuser)
@require_http_methods(["GET", "POST"])
def bulk_create_products(request):
    if request.method == "POST":
        product_list = request.POST.get("product_list", "").split("\n")
        product_list = [product.strip() for product in product_list if product.strip()]

        if product_list:
            for product in product_list:
                async_task(schedule_products_creation, product)
            messages.success(request, "Product creation task has been queued.")
        else:
            messages.error(request, "No valid products were provided.")

        return redirect("bulk_create_products")

    return render(request, "pages/bulk_create_products.html")


@require_http_methods(["GET", "POST"])
def newsletter_signup(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if email:
            # Get the referrer URL from the request
            referrer_url = request.META.get("HTTP_REFERER", "https://isitketo.org")

            data = {
                "email_address": str(email),
                "referrer_url": referrer_url,
                "subscriber_type": "unactivated",
            }

            try:
                response = requests.post(
                    "https://api.buttondown.email/v1/subscribers",
                    headers={"Authorization": f"Token {settings.BUTTONDOWN_API_TOKEN}"},
                    json=data,
                    timeout=10,
                )
                response.raise_for_status()
                result = response.json()
                if "id" in result:
                    return JsonResponse({"success": True, "message": "Successfully subscribed!"})
                else:
                    logger.warning("Unexpected Buttondown API response", extra={"result": result})
                    return JsonResponse({"success": False, "message": "Subscription failed. Please try again."})
            except requests.RequestException as e:
                logger.error("Error calling Buttondown API", exc_info=True, extra={"error": str(e)})
                return JsonResponse({"success": False, "message": "An error occurred. Please try again later."})
        else:
            return JsonResponse({"success": False, "message": "Email is required."})
    return render(request, "newsletter_signup.html")
