from django.http import HttpResponse
from rest_framework import generics, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound

from catalog.models import Category, Collection, Product
from pages.models import CityPage, SitePage
from blog.models import BlogPost
from homepage.models import HomeSection
from leads.models import Dealer, Inquiry
from formbuilder.models import FormDefinition
from menus.models import Menu, MenuItem
from applications.models import ApplicationCategory, ApplicationProject
from gallery.models import GalleryCatalogue
from faq.models import Faq
from seo.models import GlobalSEO, SiteSettings, ThemeSettings
from media_library.utils import absolutize_media_urls

from .serializers import (
    CategorySerializer, CollectionSerializer,
    ProductListSerializer, ProductDetailSerializer,
    CityPageListSerializer, CityPageDetailSerializer,
    SitePageSerializer,
    BlogPostListSerializer, BlogPostDetailSerializer,
    DealerSerializer, InquiryCreateSerializer,
    FormDefinitionSerializer, FormSubmissionCreateSerializer,
)
from menus.serializers import MenuSerializer
from applications.serializers import (
    ApplicationCategorySerializer, ApplicationProjectListSerializer, ApplicationProjectDetailSerializer,
)
from gallery.serializers import GalleryCatalogueDetailSerializer
from faq.serializers import FaqSerializer
from .throttles import InquiryThrottle, FormSubmitThrottle
from .preview_tokens import verify_preview_token


# ── Products ──────────────────────────────────────────────────────────────────

class ProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class  = None  # storefront filters client-side over the full set
    filter_backends  = [filters.SearchFilter, filters.OrderingFilter]
    search_fields    = ["name", "sku", "category__name"]
    ordering_fields  = ["name", "created"]

    def get_queryset(self):
        qs = (
            Product.objects.filter(status="published")
            .select_related("category", "collection")
            .prefetch_related("product_images__asset", "related_products")
        )
        # ?category= accepts a slug ("laminates") or a name ("Thermo Laminates")
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category__slug=category) | qs.filter(category__name__iexact=category)
        collection = self.request.query_params.get("collection")
        if collection:
            qs = qs.filter(collection__slug=collection) | qs.filter(collection__name__iexact=collection)
        return qs.distinct()


class ProductDetailView(generics.RetrieveAPIView):
    queryset = (
        Product.objects.filter(status="published")
        .select_related("category", "collection", "pdf_catalog")
        .prefetch_related("product_images__asset", "related_products")
    )
    serializer_class = ProductDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field     = "slug"


class ProductPreviewDetailView(generics.RetrieveAPIView):
    """Same shape as ProductDetailView but ignores `status` and instead requires
    a signed `?token=` (minted by the CMS's Preview button) — lets the real
    Next.js page render a draft product exactly as the public site would once
    it's published. See api/preview_tokens.py. Looked up by slug (not pk) so
    the frontend page — which only ever has the slug from its URL — needs no
    extra id param."""
    queryset         = Product.objects.all()
    serializer_class = ProductDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field     = "slug"

    def get_object(self):
        obj = super().get_object()
        if not verify_preview_token("product", obj.slug, self.request.query_params.get("token", "")):
            raise NotFound("Invalid or expired preview link.")
        return obj


# ── Categories ────────────────────────────────────────────────────────────────

class CategoryListView(generics.ListAPIView):
    queryset         = Category.objects.filter(status="published")
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class  = None


# ── Collections ───────────────────────────────────────────────────────────────

class CollectionListView(generics.ListAPIView):
    queryset         = Collection.objects.filter(status="published")
    serializer_class = CollectionSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class  = None


# ── City Pages ────────────────────────────────────────────────────────────────

class CityPageListView(generics.ListAPIView):
    queryset         = CityPage.objects.filter(status="published")
    serializer_class = CityPageListSerializer
    permission_classes = [permissions.AllowAny]


class CityPageDetailView(generics.RetrieveAPIView):
    queryset         = CityPage.objects.filter(status="published")
    serializer_class = CityPageDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field     = "slug"


class CityPagePreviewDetailView(generics.RetrieveAPIView):
    """Preview counterpart of CityPageDetailView — see ProductPreviewDetailView."""
    queryset         = CityPage.objects.all()
    serializer_class = CityPageDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field     = "slug"

    def get_object(self):
        obj = super().get_object()
        if not verify_preview_token("citypage", obj.slug, self.request.query_params.get("token", "")):
            raise NotFound("Invalid or expired preview link.")
        return obj


# ── Blog ──────────────────────────────────────────────────────────────────────

class BlogPostListView(generics.ListAPIView):
    queryset         = BlogPost.objects.filter(status="published").prefetch_related("categories")
    serializer_class = BlogPostListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class  = None  # storefront renders the full list / filters client-side
    filter_backends  = [filters.SearchFilter]
    search_fields    = ["title", "categories__name"]


class BlogPostDetailView(generics.RetrieveAPIView):
    queryset         = BlogPost.objects.filter(status="published")
    serializer_class = BlogPostDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field     = "slug"


class BlogPostPreviewDetailView(generics.RetrieveAPIView):
    """Preview counterpart of BlogPostDetailView — see ProductPreviewDetailView."""
    queryset         = BlogPost.objects.all()
    serializer_class = BlogPostDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field     = "slug"

    def get_object(self):
        obj = super().get_object()
        if not verify_preview_token("blogpost", obj.slug, self.request.query_params.get("token", "")):
            raise NotFound("Invalid or expired preview link.")
        return obj


# ── Dealers ───────────────────────────────────────────────────────────────────

class DealerListView(generics.ListAPIView):
    serializer_class = DealerSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs   = Dealer.objects.filter(status="active")
        city = self.request.query_params.get("city")
        if city:
            qs = qs.filter(city__icontains=city)
        return qs


# ── Inquiries (public POST) ───────────────────────────────────────────────────

class InquiryCreateView(generics.CreateAPIView):
    serializer_class   = InquiryCreateSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes   = [InquiryThrottle]


# ── Robots.txt ────────────────────────────────────────────────────────────────

class RobotsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        content = GlobalSEO.get().robots_txt
        return HttpResponse(content, content_type="text/plain")


# ── Site Settings (public read) ───────────────────────────────────────────────

class SiteSettingsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        s = SiteSettings.get()
        seo = GlobalSEO.get()
        theme = ThemeSettings.get()
        data = {
            "site_name":    s.site_name,
            "tagline":      s.tagline,
            "logo_dark_url":  s.logo_dark_url,
            "logo_light_url": s.logo_light_url,
            "favicon_url":  s.favicon_url,
            "phone_primary":   s.phone_primary,
            "phone_secondary": s.phone_secondary,
            "email_primary":   s.email_primary,
            "email_secondary": s.email_secondary,
            "address_line1":  s.address_line1,
            "address_line2":  s.address_line2,
            "city":    s.city,
            "state":   s.state,
            "pincode": s.pincode,
            "working_hours": s.working_hours,
            "full_address":  s.full_address(),
            "map_embed_url": s.map_embed_url,
            "map_lat": str(s.map_lat) if s.map_lat else None,
            "map_lng": str(s.map_lng) if s.map_lng else None,
            "social": {
                "instagram": s.instagram_url,
                "facebook":  s.facebook_url,
                "youtube":   s.youtube_url,
                "pinterest": s.pinterest_url,
                "linkedin":  s.linkedin_url,
                "twitter":   s.twitter_url,
                "whatsapp":  s.whatsapp_number,
            },
            "header": {
                "topbar_badge":    s.topbar_badge,
                "cta_label":       s.header_cta_label,
                "cta_url":         s.header_cta_url,
            },
            "footer": {
                "description":       s.footer_description,
                "copyright":         s.footer_copyright,
                "newsletter_text":   s.footer_newsletter_text,
            },
            "analytics": {
                "ga4_id":           seo.ga4_code,
                "gtm_id":           seo.gtm_code,
                "fb_pixel_id":      seo.fb_pixel_code,
                "clarity_id":       seo.clarity_code,
                "gsc_verification": seo.gsc_verification_code,
            },
            "recaptcha": {
                "version":  seo.recaptcha_version,
                "site_key": seo.recaptcha_site_key if seo.recaptcha_version != GlobalSEO.RECAPTCHA_OFF else "",
            },
            "theme": {
                "colors": {
                    "primary":      theme.primary_color,
                    "secondary":    theme.secondary_color,
                    "accent":       theme.accent_color,
                    "heading":      theme.heading_color,
                    "text":         theme.text_color,
                    "link":         theme.link_color,
                    "link_hover":   theme.link_hover_color,
                    "background":   theme.background_color,
                    "header_bg":    theme.header_bg_color,
                    "footer_bg":    theme.footer_bg_color,
                    "footer_text":  theme.footer_text_color,
                },
                "typography": {
                    "heading_font":   theme.heading_font,
                    "body_font":      theme.body_font,
                    "base_font_size": theme.base_font_size,
                },
                "buttons": {
                    "style":         theme.button_style,
                    "radius":        theme.button_radius,
                    "hover_effect":  theme.button_hover_effect,
                    "text_color":    theme.button_text_color,
                },
                "layout": {
                    "container_max_width": theme.container_max_width,
                    "border_radius":       theme.border_radius,
                    "card_shadow_style":   theme.card_shadow_style,
                },
                "css_vars": theme.as_css_vars(),
            },
        }
        return Response(data)


# ── Nav Links (public read) ───────────────────────────────────────────────────

NAV_LINK_MENU_SLUGS = ["main", "topbar", "mega_quick", "footer_company"]


class NavLinksView(APIView):
    """The live Header/Top Bar/Mega Menu/Footer links — backed by the
    system menus of the same slugs, managed in the CMS's single "Menus"
    screen (see ``menus.models.Menu.is_system``)."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        items = MenuItem.objects.filter(
            menu__slug__in=NAV_LINK_MENU_SLUGS, active=True, parent=None,
        ).select_related("menu")
        by_group: dict = {}
        for item in items:
            by_group.setdefault(item.menu.slug, []).append({
                "label":        item.label,
                "url":          item.url,
                "open_new_tab": item.open_new_tab,
                "position":     item.position,
            })
        return Response(by_group)


# ── Home Page blocks (public read) ────────────────────────────────────────────

class HomePageView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        sections = HomeSection.objects.filter(enabled=True)  # Meta.ordering applies
        return Response({
            "sections": [
                {
                    "block_type": s.block_type,
                    "anchor_id":  s.anchor_id,
                    "content":    absolutize_media_urls(s.resolved(), request),
                }
                for s in sections
            ],
        })


class SitePageView(generics.RetrieveAPIView):
    """Public read for one CMS-managed page's blocks — ``GET /api/pages/<slug>/``.

    Draft (unpublished) pages 404 here, same as if they didn't exist.
    """
    queryset           = SitePage.objects.filter(is_published=True).prefetch_related("sections")
    serializer_class   = SitePageSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field       = "slug"


# ── Forms (CMS-managed, arbitrary field sets) ─────────────────────────────────

class FormDefinitionView(generics.RetrieveAPIView):
    """Public read for one form's field schema — ``GET /api/forms/<slug>/``."""
    queryset           = FormDefinition.objects.prefetch_related("fields")
    serializer_class   = FormDefinitionSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field       = "slug"


class FormSubmitView(generics.CreateAPIView):
    """Public submit for a CMS-managed form — ``POST /api/forms/<slug>/submit/``.

    Routes to ``leads.Inquiry`` (same pipeline the Leads dashboard already
    reads) when the form's ``target_pipeline`` says so — how a form that used
    to be hard-coded (Contact, the site-wide popup, …) becomes CMS field-
    editable without changing where its submissions end up.
    """
    serializer_class   = FormSubmissionCreateSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes   = [FormSubmitThrottle]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data["slug"] = self.kwargs["slug"]
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        form = serializer.validated_data["form"]
        if form.target_pipeline == FormDefinition.TARGET_INQUIRY:
            from formbuilder.services import route_submission_to_inquiry
            route_submission_to_inquiry(
                form,
                serializer.validated_data.get("data") or {},
                serializer.validated_data.get("source_page", ""),
            )
            return Response({"ok": True}, status=201)

        serializer.save()
        return Response(serializer.data, status=201)


# ── Menus (CMS-managed, hierarchical) ─────────────────────────────────────────

class MenuView(generics.RetrieveAPIView):
    """Public read for one hierarchical menu — ``GET /api/menus/<slug>/``.
    ``NavLinksView`` below is a flattened, grouped shortcut over the same
    data for the system Header/Top Bar/Mega Menu/Footer menus."""
    queryset           = Menu.objects.prefetch_related("items__children")
    serializer_class   = MenuSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field       = "slug"


# ── Applications (CMS-managed use-case categories + case studies) ────────────

class ApplicationCategoryListView(generics.ListAPIView):
    """Public read — ``GET /api/applications/categories/``."""
    queryset           = ApplicationCategory.objects.filter(enabled=True)
    serializer_class   = ApplicationCategorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class   = None


class ApplicationProjectListView(generics.ListAPIView):
    """Public read, optionally filtered — ``GET /api/applications/projects/?category=<slug>``."""
    serializer_class   = ApplicationProjectListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class   = None

    def get_queryset(self):
        qs = ApplicationProject.objects.filter(enabled=True).select_related("category")
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category__slug=category)
        return qs


class ApplicationProjectDetailView(generics.RetrieveAPIView):
    """Public read — ``GET /api/applications/projects/<slug>/``."""
    queryset           = ApplicationProject.objects.filter(enabled=True).select_related("category")
    serializer_class   = ApplicationProjectDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field       = "slug"


# ── Design Gallery (the real /applications page's catalogues) ────────────────

class GalleryCatalogueListView(generics.ListAPIView):
    """Public read — ``GET /api/gallery/catalogues/``. Returns full image
    lists per catalogue in one call (mirrors the old build-time manifest,
    which was also one full read — only ~350 images total, so this stays
    small). Catalogues with zero enabled images are omitted, matching the
    old manifest behaviour."""
    serializer_class   = GalleryCatalogueDetailSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class   = None

    def get_queryset(self):
        return [
            c for c in GalleryCatalogue.objects.filter(enabled=True).prefetch_related("images")
            if c.images.filter(enabled=True).exists()
        ]


class GalleryCatalogueDetailView(generics.RetrieveAPIView):
    """Public read — ``GET /api/gallery/catalogues/<slug>/``."""
    queryset           = GalleryCatalogue.objects.filter(enabled=True).prefetch_related("images")
    serializer_class   = GalleryCatalogueDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field       = "slug"


# ── FAQs (CMS-managed, gathered from blog posts) ──────────────────────────────

class FaqListView(generics.ListAPIView):
    """Public read — ``GET /api/faqs/``. Active entries, ordered."""
    queryset           = Faq.objects.filter(is_active=True).select_related("source_post")
    serializer_class   = FaqSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class   = None
