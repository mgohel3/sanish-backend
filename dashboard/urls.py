from django.urls import path
from accounts.views import LoginView, LogoutView, VerifyOTPView, ResendOTPView
from dashboard.views.home import HomeView
from dashboard.views.products import (
    ProductListView, ProductCreateView, ProductEditView, ProductDeleteView,
    ProductBulkDeleteView, ProductBulkStatusView, ProductPreviewView, ProductExportView, ProductImportView,
    AttributeOptionAddView, AttributeOptionDeleteView, AttributeOptionReorderView,
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
from dashboard.views.seo_views import GlobalSEOView, RedirectListView, SchemaGeneratorView, SiteSettingsView, ThemeSettingsView
from dashboard.views.blog import (
    BlogPostListView, BlogPostCreateView, BlogPostEditView,
    BlogPostDeleteView, BlogPostBulkDeleteView, BlogCategoryListView, BlogPostPreviewView,
)
from dashboard.views.leads import (
    InquiryListView, DealerListView, DealerCreateView, DealerEditView,
)
from dashboard.views.media import MediaLibraryView, MediaUploadAjaxView, MediaPickerListView
from dashboard.views.users import UserListView, UserCreateView, UserEditView, ActivityLogView
from dashboard.views.homepage import (
    HomeSectionListView, HomeSectionReorderView, HomeSectionToggleView,
    HomeSectionCreateView, HomeSectionEditView, HomeSectionDeleteView,
)
from dashboard.views.seo_health import SEOHealthView
from dashboard.views.pages import (
    SitePageListView, SitePageCreateView, SitePageDeleteView, SitePageToggleView,
    PageSectionListView, PageSectionReorderView,
    PageSectionToggleView, PageSectionCreateView, PageSectionEditView,
    PageSectionDeleteView,
)
from dashboard.views.forms import (
    FormListView, FormCreateView, FormSettingsEditView, FormDeleteView,
    FormFieldListView, FormFieldReorderView, FormFieldCreateView,
    FormFieldEditView, FormFieldDeleteView, FormSubmissionListView,
)
from dashboard.views.menus import (
    MenuListView, MenuCreateView, MenuEditView, MenuDeleteView,
    MenuItemListView, MenuItemReorderView, MenuItemCreateView,
    MenuItemEditView, MenuItemDeleteView,
)
from dashboard.views.applications import (
    ApplicationCategoryListView, ApplicationCategoryCreateView,
    ApplicationCategoryEditView, ApplicationCategoryDeleteView,
    ApplicationProjectListView, ApplicationProjectCreateView,
    ApplicationProjectEditView, ApplicationProjectDeleteView,
)
from dashboard.views.gallery import (
    GalleryCatalogueListView, GalleryCatalogueCreateView,
    GalleryCatalogueEditView, GalleryCatalogueDeleteView,
    GalleryImageListView, GalleryImageUploadView,
    GalleryImageReorderView, GalleryImageDeleteView,
)
from dashboard.views.faq import (
    FaqListView, FaqCreateView, FaqEditView, FaqDeleteView,
    FaqReorderView, FaqToggleView,
)
from dashboard.views.help import HelpIndexView, HelpArticleView

urlpatterns = [
    # Auth
    path("auth/login/",       LoginView.as_view(),      name="cms_login"),
    path("auth/verify-otp/",  VerifyOTPView.as_view(),  name="cms_verify_otp"),
    path("auth/resend-otp/",  ResendOTPView.as_view(),  name="cms_resend_otp"),
    path("auth/logout/",      LogoutView.as_view(),     name="cms_logout"),

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
    path("products/bulk-delete/",      ProductBulkDeleteView.as_view(), name="product_bulk_delete"),
    path("products/bulk-status/",      ProductBulkStatusView.as_view(), name="product_bulk_status"),
    path("products/attributes/<str:attribute>/add/",     AttributeOptionAddView.as_view(),     name="attribute_option_add"),
    path("products/attributes/<str:attribute>/delete/",  AttributeOptionDeleteView.as_view(),  name="attribute_option_delete"),
    path("products/attributes/<str:attribute>/reorder/", AttributeOptionReorderView.as_view(), name="attribute_option_reorder"),

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
    path("theme/",             ThemeSettingsView.as_view(), name="theme_settings"),

    # Blog
    path("blog/",              BlogPostListView.as_view(),    name="blog_list"),
    path("blog/create/",       BlogPostCreateView.as_view(),  name="blog_post_create"),
    path("blog/<int:pk>/",     BlogPostEditView.as_view(),    name="blog_post_edit"),
    path("blog/<int:pk>/delete/",  BlogPostDeleteView.as_view(),  name="blog_post_delete"),
    path("blog/<int:pk>/preview/", BlogPostPreviewView.as_view(), name="blog_post_preview"),
    path("blog/categories/",   BlogCategoryListView.as_view(), name="blog_categories"),
    path("blog/bulk-delete/",  BlogPostBulkDeleteView.as_view(), name="blog_bulk_delete"),

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
    path("pages/create/",                   SitePageCreateView.as_view(),      name="site_page_create"),
    path("pages/<slug:slug>/delete/",       SitePageDeleteView.as_view(),      name="site_page_delete"),
    path("pages/<slug:slug>/toggle/",       SitePageToggleView.as_view(),      name="site_page_toggle"),
    path("pages/<slug:slug>/",              PageSectionListView.as_view(),     name="page_section_list"),
    path("pages/<slug:slug>/reorder/",      PageSectionReorderView.as_view(),  name="page_section_reorder"),
    path("pages/<slug:slug>/create/",       PageSectionCreateView.as_view(),   name="page_section_create"),
    path("pages/<slug:slug>/<int:pk>/",     PageSectionEditView.as_view(),     name="page_section_edit"),
    path("pages/<slug:slug>/<int:pk>/toggle/", PageSectionToggleView.as_view(), name="page_section_toggle"),
    path("pages/<slug:slug>/<int:pk>/delete/", PageSectionDeleteView.as_view(), name="page_section_delete"),

    # Forms (generic field builder — any form on the site)
    path("forms/",                       FormListView.as_view(),           name="form_list"),
    path("forms/create/",                FormCreateView.as_view(),         name="form_create"),
    path("forms/<slug:slug>/settings/",  FormSettingsEditView.as_view(),   name="form_settings_edit"),
    path("forms/<slug:slug>/delete/",    FormDeleteView.as_view(),         name="form_delete"),
    path("forms/<slug:slug>/",           FormFieldListView.as_view(),      name="form_field_list"),
    path("forms/<slug:slug>/reorder/",   FormFieldReorderView.as_view(),   name="form_field_reorder"),
    path("forms/<slug:slug>/create/",    FormFieldCreateView.as_view(),    name="form_field_create"),
    path("forms/<slug:slug>/<int:pk>/",         FormFieldEditView.as_view(),   name="form_field_edit"),
    path("forms/<slug:slug>/<int:pk>/delete/",  FormFieldDeleteView.as_view(), name="form_field_delete"),
    path("forms/<slug:slug>/submissions/",      FormSubmissionListView.as_view(), name="form_submission_list"),

    # Menus (hierarchical, WordPress-style — the single screen for all site navigation,
    # including the system Header/Top Bar/Mega Menu/Footer menus)
    path("menus/",                      MenuListView.as_view(),        name="menu_list"),
    path("menus/create/",               MenuCreateView.as_view(),      name="menu_create"),
    path("menus/<slug:slug>/edit/",     MenuEditView.as_view(),        name="menu_edit"),
    path("menus/<slug:slug>/delete/",   MenuDeleteView.as_view(),      name="menu_delete"),
    path("menus/<slug:slug>/",          MenuItemListView.as_view(),    name="menu_item_list"),
    path("menus/<slug:slug>/reorder/",  MenuItemReorderView.as_view(), name="menu_item_reorder"),
    path("menus/<slug:slug>/create/",   MenuItemCreateView.as_view(),  name="menu_item_create"),
    path("menus/<slug:slug>/<int:pk>/",         MenuItemEditView.as_view(),   name="menu_item_edit"),
    path("menus/<slug:slug>/<int:pk>/delete/",  MenuItemDeleteView.as_view(), name="menu_item_delete"),
    path("menus/<slug:slug>/<int:parent_pk>/children/",          MenuItemListView.as_view(),    name="menu_item_children"),
    path("menus/<slug:slug>/<int:parent_pk>/children/reorder/",  MenuItemReorderView.as_view(), name="menu_item_children_reorder"),
    path("menus/<slug:slug>/<int:parent_pk>/children/create/",   MenuItemCreateView.as_view(),  name="menu_item_child_create"),

    # SEO Health
    path("seo/health/", SEOHealthView.as_view(), name="seo_health"),

    # Applications (use-case categories + case studies — like Products)
    path("applications/",                     ApplicationCategoryListView.as_view(),   name="application_category_list"),
    path("applications/create/",              ApplicationCategoryCreateView.as_view(), name="application_category_create"),
    path("applications/<int:pk>/",            ApplicationCategoryEditView.as_view(),   name="application_category_edit"),
    path("applications/<int:pk>/delete/",     ApplicationCategoryDeleteView.as_view(), name="application_category_delete"),
    path("applications/projects/",            ApplicationProjectListView.as_view(),    name="application_project_list"),
    path("applications/projects/create/",     ApplicationProjectCreateView.as_view(),  name="application_project_create"),
    path("applications/projects/<int:pk>/",   ApplicationProjectEditView.as_view(),    name="application_project_edit"),
    path("applications/projects/<int:pk>/delete/", ApplicationProjectDeleteView.as_view(), name="application_project_delete"),

    # Design Gallery (the real /applications catalogues — S'Shades, Thre3, Cool Colour, …)
    path("gallery/",                          GalleryCatalogueListView.as_view(),    name="gallery_catalogue_list"),
    path("gallery/create/",                   GalleryCatalogueCreateView.as_view(),  name="gallery_catalogue_create"),
    path("gallery/<int:pk>/settings/",        GalleryCatalogueEditView.as_view(),    name="gallery_catalogue_edit"),
    path("gallery/<int:pk>/delete/",          GalleryCatalogueDeleteView.as_view(),  name="gallery_catalogue_delete"),
    path("gallery/<int:pk>/",                 GalleryImageListView.as_view(),        name="gallery_image_list"),
    path("gallery/<int:pk>/upload/",          GalleryImageUploadView.as_view(),      name="gallery_image_upload"),
    path("gallery/<int:pk>/reorder/",         GalleryImageReorderView.as_view(),     name="gallery_image_reorder"),
    path("gallery/<int:pk>/images/<int:image_id>/delete/", GalleryImageDeleteView.as_view(), name="gallery_image_delete"),

    # FAQs
    path("faqs/",              FaqListView.as_view(),     name="faq_list"),
    path("faqs/reorder/",      FaqReorderView.as_view(),  name="faq_reorder"),
    path("faqs/create/",       FaqCreateView.as_view(),   name="faq_create"),
    path("faqs/<int:pk>/",     FaqEditView.as_view(),     name="faq_edit"),
    path("faqs/<int:pk>/delete/", FaqDeleteView.as_view(), name="faq_delete"),
    path("faqs/<int:pk>/toggle/", FaqToggleView.as_view(), name="faq_toggle"),

    # Help
    path("help/", HelpIndexView.as_view(), name="help_index"),
    path("help/<slug:slug>/", HelpArticleView.as_view(), name="help_article"),
]
