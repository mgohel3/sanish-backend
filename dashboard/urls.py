from django.urls import path
from accounts.views import LoginView, LogoutView
from dashboard.views.home import HomeView
from dashboard.views.products import (
    ProductListView, ProductCreateView, ProductEditView, ProductDeleteView,
    ProductPreviewView, ProductExportView, ProductImportView,
)
from dashboard.views.categories import (
    CategoryListView, CategoryCreateView, CategoryEditView, CategoryDeleteView,
    CollectionListView, CollectionCreateView, CollectionEditView, CollectionDeleteView,
)
from dashboard.views.city_pages import (
    CityPageIndexView, CityPageListView, CityPageCreateView,
    CityPageEditView, CityPageDeleteView, CityPagePreviewView,
    BulkImportView,
    PageTemplateListView, PageTemplateCreateView, PageTemplateEditView,
)
from dashboard.views.seo_views import GlobalSEOView, RedirectListView, SchemaGeneratorView, SiteSettingsView
from dashboard.views.blog import (
    BlogPostListView, BlogPostCreateView, BlogPostEditView,
    BlogPostDeleteView, BlogCategoryListView, BlogPostPreviewView,
)
from dashboard.views.leads import (
    InquiryListView, DealerListView, DealerCreateView, DealerEditView,
)
from dashboard.views.media import MediaLibraryView, MediaUploadAjaxView, MediaPickerListView
from dashboard.views.users import UserListView, UserCreateView, UserEditView, ActivityLogView
from dashboard.views.nav_views import NavLinkListView, NavLinkCreateView, NavLinkEditView, NavLinkDeleteView
from dashboard.views.homepage import (
    HomeSectionListView, HomeSectionReorderView, HomeSectionToggleView,
    HomeSectionCreateView, HomeSectionEditView, HomeSectionDeleteView,
)
from dashboard.views.seo_health import SEOHealthView
from dashboard.views.pages import (
    SitePageListView, PageSectionListView, PageSectionReorderView,
    PageSectionToggleView, PageSectionCreateView, PageSectionEditView,
    PageSectionDeleteView,
)

urlpatterns = [
    # Auth
    path("auth/login/",  LoginView.as_view(),  name="cms_login"),
    path("auth/logout/", LogoutView.as_view(), name="cms_logout"),

    # Home
    path("", HomeView.as_view(), name="cms_home"),

    # Products
    path("products/",              ProductListView.as_view(),   name="product_list"),
    path("products/export/",       ProductExportView.as_view(), name="product_export"),
    path("products/import/",       ProductImportView.as_view(), name="product_import"),
    path("products/create/",       ProductCreateView.as_view(), name="product_create"),
    path("products/<int:pk>/",     ProductEditView.as_view(),   name="product_edit"),
    path("products/<int:pk>/delete/",  ProductDeleteView.as_view(),  name="product_delete"),
    path("products/<int:pk>/preview/", ProductPreviewView.as_view(), name="product_preview"),

    # Categories
    path("categories/",              CategoryListView.as_view(),   name="category_list"),
    path("categories/create/",       CategoryCreateView.as_view(), name="category_create"),
    path("categories/<int:pk>/",     CategoryEditView.as_view(),   name="category_edit"),
    path("categories/<int:pk>/delete/", CategoryDeleteView.as_view(), name="category_delete"),

    # Collections
    path("collections/",              CollectionListView.as_view(),   name="collection_list"),
    path("collections/create/",       CollectionCreateView.as_view(), name="collection_create"),
    path("collections/<int:pk>/",     CollectionEditView.as_view(),   name="collection_edit"),
    path("collections/<int:pk>/delete/", CollectionDeleteView.as_view(), name="collection_delete"),

    # City Pages
    path("city-pages/",                 CityPageIndexView.as_view(),  name="city_page_index"),
    path("city-pages/list/",            CityPageListView.as_view(),   name="city_page_list"),
    path("city-pages/create/",          CityPageCreateView.as_view(), name="city_page_create"),
    path("city-pages/<int:pk>/",        CityPageEditView.as_view(),   name="city_page_edit"),
    path("city-pages/<int:pk>/delete/",  CityPageDeleteView.as_view(),  name="city_page_delete"),
    path("city-pages/<int:pk>/preview/", CityPagePreviewView.as_view(), name="city_page_preview"),
    path("city-pages/bulk-import/",     BulkImportView.as_view(),     name="city_page_bulk_import"),
    path("city-pages/templates/",       PageTemplateListView.as_view(),  name="page_template_list"),
    path("city-pages/templates/create/", PageTemplateCreateView.as_view(), name="page_template_create"),
    path("city-pages/templates/<int:pk>/", PageTemplateEditView.as_view(), name="page_template_edit"),

    # SEO
    path("seo/",               GlobalSEOView.as_view(),    name="seo_global"),
    path("seo/redirects/",     RedirectListView.as_view(), name="seo_redirects"),
    path("seo/schema/",        SchemaGeneratorView.as_view(), name="seo_schema"),
    path("seo/site-settings/", SiteSettingsView.as_view(), name="site_settings"),

    # Blog
    path("blog/",              BlogPostListView.as_view(),    name="blog_list"),
    path("blog/create/",       BlogPostCreateView.as_view(),  name="blog_post_create"),
    path("blog/<int:pk>/",     BlogPostEditView.as_view(),    name="blog_post_edit"),
    path("blog/<int:pk>/delete/",  BlogPostDeleteView.as_view(),  name="blog_post_delete"),
    path("blog/<int:pk>/preview/", BlogPostPreviewView.as_view(), name="blog_post_preview"),
    path("blog/categories/",   BlogCategoryListView.as_view(), name="blog_categories"),

    # Leads
    path("leads/",               InquiryListView.as_view(),  name="inquiry_list"),
    path("leads/dealers/",       DealerListView.as_view(),   name="dealer_list"),
    path("leads/dealers/create/", DealerCreateView.as_view(), name="dealer_create"),
    path("leads/dealers/<int:pk>/", DealerEditView.as_view(), name="dealer_edit"),

    # Media
    path("media/",        MediaLibraryView.as_view(),    name="media_library"),
    path("media/upload/", MediaUploadAjaxView.as_view(), name="media_upload_ajax"),
    path("media/picker/", MediaPickerListView.as_view(), name="media_picker_list"),

    # Users
    path("users/",              UserListView.as_view(),    name="user_list"),
    path("users/create/",       UserCreateView.as_view(),  name="user_create"),
    path("users/<int:pk>/",     UserEditView.as_view(),    name="user_edit"),
    path("users/activity-log/", ActivityLogView.as_view(), name="activity_log"),

    # Home Page blocks
    path("home-page/",                   HomeSectionListView.as_view(),    name="home_section_list"),
    path("home-page/reorder/",           HomeSectionReorderView.as_view(), name="home_section_reorder"),
    path("home-page/create/",            HomeSectionCreateView.as_view(),  name="home_section_create"),
    path("home-page/<int:pk>/",          HomeSectionEditView.as_view(),    name="home_section_edit"),
    path("home-page/<int:pk>/toggle/",   HomeSectionToggleView.as_view(),  name="home_section_toggle"),
    path("home-page/<int:pk>/delete/",   HomeSectionDeleteView.as_view(),  name="home_section_delete"),

    # Pages (generic block builder — About Us, Contact Us, Rewards, …)
    path("pages/",                          SitePageListView.as_view(),        name="site_page_list"),
    path("pages/<slug:slug>/",              PageSectionListView.as_view(),     name="page_section_list"),
    path("pages/<slug:slug>/reorder/",      PageSectionReorderView.as_view(),  name="page_section_reorder"),
    path("pages/<slug:slug>/create/",       PageSectionCreateView.as_view(),   name="page_section_create"),
    path("pages/<slug:slug>/<int:pk>/",     PageSectionEditView.as_view(),     name="page_section_edit"),
    path("pages/<slug:slug>/<int:pk>/toggle/", PageSectionToggleView.as_view(), name="page_section_toggle"),
    path("pages/<slug:slug>/<int:pk>/delete/", PageSectionDeleteView.as_view(), name="page_section_delete"),

    # Navigation Links
    path("navigation/",              NavLinkListView.as_view(),   name="nav_link_list"),
    path("navigation/create/",       NavLinkCreateView.as_view(), name="nav_link_create"),
    path("navigation/<int:pk>/",     NavLinkEditView.as_view(),   name="nav_link_edit"),
    path("navigation/<int:pk>/delete/", NavLinkDeleteView.as_view(), name="nav_link_delete"),

    # SEO Health
    path("seo/health/", SEOHealthView.as_view(), name="seo_health"),
]
