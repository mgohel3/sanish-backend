"""
Server-side JSON-LD schema generators.
Each function returns a Python dict; call json.dumps() to get the string.
"""
import json


def generate_schema_json(schema_type, **kwargs):
    generators = {
        "LocalBusiness":  _local_business,
        "Product":        _product,
        "FAQPage":        _faq_page,
        "Organization":   _organization,
        "Article":        _article,
        "BreadcrumbList": _breadcrumb,
    }
    fn = generators.get(schema_type, _local_business)
    return json.dumps(fn(**kwargs), indent=2)


def _local_business(city="", state="", product="", page_url="", title="", **kw):
    return {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": f"Sanish Laminate — {product} in {city}",
        "description": f"Premium {product} suppliers and dealers in {city}, {state}.",
        "url": page_url,
        "address": {
            "@type": "PostalAddress",
            "addressLocality": city,
            "addressRegion": state,
            "addressCountry": "IN",
        },
    }


def _product(title="", page_url="", product="", **kw):
    return {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": title or product,
        "brand": {"@type": "Brand", "name": "Sanish Laminate"},
        "url": page_url,
    }


def _faq_page(faqs=None, **kw):
    faqs = faqs or []
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": faq.get("q", ""),
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": faq.get("a", ""),
                },
            }
            for faq in faqs
        ],
    }


def _organization(**kw):
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Sanish Laminate",
        "url": "https://sanishlaminate.com",
        "logo": "https://sanishlaminate.com/logo.png",
        "sameAs": [
            "https://www.facebook.com/sanishlaminate/",
            "https://www.instagram.com/sanishlaminate/",
            "https://www.youtube.com/@SanishLaminate",
            "https://www.linkedin.com/company/sanish-laminate-company/",
        ],
    }


def _article(title="", page_url="", **kw):
    return {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "publisher": {
            "@type": "Organization",
            "name": "Sanish Laminate",
        },
        "url": page_url,
    }


def _breadcrumb(breadcrumbs=None, **kw):
    breadcrumbs = breadcrumbs or []
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": crumb.get("name", ""),
                "item": crumb.get("url", ""),
            }
            for i, crumb in enumerate(breadcrumbs)
        ],
    }
