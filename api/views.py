from django.http import HttpResponse
from rest_framework import generics, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView

from catalog.models import Category, Collection, Product
from pages.models import CityPage
from blog.models import BlogPost
from leads.models import Dealer, Inquiry
from seo.models import GlobalSEO, SiteSettings, NavLink

from .serializers import (
    CategorySerializer, CollectionSerializer,
    ProductListSerializer, ProductDetailSerializer,
    CityPageListSerializer, CityPageDetailSerializer,
    BlogPostListSerializer, BlogPostDetailSerializer,
    DealerSerializer, InquiryCreateSerializer,
)
from .throttles import InquiryThrottle


# ── Products ──────────────────────────────────────────────────────────────────

class ProductListView(generics.ListAPIView):
    queryset         = Product.objects.filter(status="published").select_related("category", "collection")
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends  = [filters.SearchFilter, filters.OrderingFilter]
    search_fields    = ["name", "sku", "category__name"]
    ordering_fields  = ["name", "created"]


class ProductDetailView(generics.RetrieveAPIView):
    queryset         = Product.objects.filter(status="published")
    serializer_class = ProductDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field     = "slug"


# ── Categories ────────────────────────────────────────────────────────────────

class CategoryListView(generics.ListAPIView):
    queryset         = Category.objects.filter(status="published")
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


# ── Collections ───────────────────────────────────────────────────────────────

class CollectionListView(generics.ListAPIView):
    queryset         = Collection.objects.filter(status="published")
    serializer_class = CollectionSerializer
    permission_classes = [permissions.AllowAny]


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


# ── Blog ──────────────────────────────────────────────────────────────────────

class BlogPostListView(generics.ListAPIView):
    queryset         = BlogPost.objects.filter(status="published")
    serializer_class = BlogPostListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends  = [filters.SearchFilter]
    search_fields    = ["title", "categories__name"]


class BlogPostDetailView(generics.RetrieveAPIView):
    queryset         = BlogPost.objects.filter(status="published")
    serializer_class = BlogPostDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field     = "slug"


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
        }
        return Response(data)


# ── Nav Links (public read) ───────────────────────────────────────────────────

class NavLinksView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        links = NavLink.objects.filter(active=True)
        by_group: dict = {}
        for lnk in links:
            by_group.setdefault(lnk.group, []).append({
                "label":        lnk.label,
                "url":          lnk.url,
                "open_new_tab": lnk.open_new_tab,
                "position":     lnk.position,
            })
        return Response(by_group)
