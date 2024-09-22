from django.urls import path

from core import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("products/", views.ProductsView.as_view(), name="products"),
    path("categories/", views.ProductCategories.as_view(), name="product_categories"),
    path("search/", views.search_products, name="search_products"),
    path("bulk-create-products", views.bulk_create_products, name="bulk_create_products"),
    path("category/<str:category>/", views.ProductCategoryListView.as_view(), name="product_category_list"),
    path("<slug:slug>", views.ProductView.as_view(), name="product"),
]
