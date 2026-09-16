from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    ProductListView, ProductDetailView,
    CategoryListView, CollectionListView,
    CityPageListView, CityPageDetailView,
    BlogPostListView, BlogPostDetailView,
    DealerListView, InquiryCreateView,
    RobotsView, SiteSettingsView, NavLinksView, HomePageView, SitePageView,
    FormDefinitionView, FormSubmitView, MenuView,
    ApplicationCategoryListView, ApplicationProjectListView, ApplicationProjectDetailView,
    GalleryCatalogueListView, GalleryCatalogueDetailView,
    FaqListView,
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
    # Home page blocks (public read — ordered, enabled only)
    path("homepage/", HomePageView.as_view(), name="api_homepage"),
    # CMS-managed page blocks (public read — ordered, enabled only)
    path("pages/<slug:slug>/", SitePageView.as_view(), name="api_site_page"),
    # CMS-managed forms (public read of schema + public submit)
    path("forms/<slug:slug>/",        FormDefinitionView.as_view(), name="api_form_detail"),
    path("forms/<slug:slug>/submit/", FormSubmitView.as_view(),     name="api_form_submit"),
    # CMS-managed hierarchical menus (public read)
    path("menus/<slug:slug>/", MenuView.as_view(), name="api_menu_detail"),
    # Applications (use-case categories + case studies)
    path("applications/categories/",       ApplicationCategoryListView.as_view(),  name="api_application_categories"),
    path("applications/projects/",         ApplicationProjectListView.as_view(),   name="api_application_projects"),
    path("applications/projects/<slug:slug>/", ApplicationProjectDetailView.as_view(), name="api_application_project_detail"),
    # Design Gallery (the real /applications catalogues — S'Shades, Thre3, etc.)
    path("gallery/catalogues/",             GalleryCatalogueListView.as_view(),   name="api_gallery_catalogues"),
    path("gallery/catalogues/<slug:slug>/", GalleryCatalogueDetailView.as_view(), name="api_gallery_catalogue_detail"),
    # FAQs (public read — CMS-managed, gathered from blog posts)
    path("faqs/", FaqListView.as_view(), name="api_faqs"),
]
