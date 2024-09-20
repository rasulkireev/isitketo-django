from django.urls import path

from core.views import HomeView, ProductCategories, ProductCategoryListView, ProductsView, ProductView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("products/", ProductsView.as_view(), name="products"),
    path("categories/", ProductCategories.as_view(), name="product_categories"),
    path("category/<str:category>/", ProductCategoryListView.as_view(), name="product_category_list"),
    path("<slug:slug>", ProductView.as_view(), name="product"),
]
