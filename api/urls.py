from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    ProductListView, ProductDetailView,
    CategoryListView, CollectionListView,
    CityPageListView, CityPageDetailView,
    BlogPostListView, BlogPostDetailView,
    DealerListView, InquiryCreateView,
    RobotsView, SiteSettingsView, NavLinksView,
)

urlpatterns = [
    # Products
    path("products/",             ProductListView.as_view(),   name="api_products"),
    path("products/<slug:slug>/", ProductDetailView.as_view(), name="api_product_detail"),
    # Categories & Collections
    path("categories/",   CategoryListView.as_view(),   name="api_categories"),
    path("collections/",  CollectionListView.as_view(),  name="api_collections"),
    # City pages
    path("city-pages/",             CityPageListView.as_view(),   name="api_city_pages"),
    path("city-pages/<slug:slug>/", CityPageDetailView.as_view(), name="api_city_page_detail"),
    # Blog
    path("blog/",             BlogPostListView.as_view(),   name="api_blog"),
    path("blog/<slug:slug>/", BlogPostDetailView.as_view(), name="api_blog_detail"),
    # Dealers & Inquiries
    path("dealers/",    DealerListView.as_view(),    name="api_dealers"),
    path("inquiries/",  InquiryCreateView.as_view(), name="api_inquiries"),
    # Auth (JWT)
    path("token/",         TokenObtainPairView.as_view(),  name="token_obtain"),
    path("token/refresh/", TokenRefreshView.as_view(),     name="token_refresh"),
    # Robots
    path("robots.txt", RobotsView.as_view(), name="robots_txt"),
    # Site Settings (public read for frontend)
    path("site-settings/", SiteSettingsView.as_view(), name="api_site_settings"),
    # Nav Links (public read — groups: main/topbar/mega_quick/footer_company)
    path("nav-links/", NavLinksView.as_view(), name="api_nav_links"),
]
