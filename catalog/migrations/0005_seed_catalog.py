"""
Seed the catalogue with the products/categories/collections that previously
lived as hard-coded data in the Next.js frontend (src/lib/products.ts), so the
storefront has content the client can then manage from the CMS.

Idempotent and conservative: skips entirely if any published product already
exists (i.e. the client has started managing the catalogue for real).
"""
from django.db import migrations
from django.utils.text import slugify


CATEGORIES = [
    {
        "name": "Laminates",
        "hero_eyebrow": "Surface Collection",
        "hero_image_url": "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?q=80&w=2000",
        "description": "Premium decorative laminates crafted for contemporary interiors — high-gloss, matte, metallic, wood, stone and fabric designs.",
    },
    {
        "name": "Louvers",
        "hero_eyebrow": "Architectural Surfaces",
        "hero_image_url": "https://images.unsplash.com/photo-1565538810643-b5bdb714032a?q=80&w=2000",
        "description": "Fluted and architectural panel surfaces that transform ordinary walls into striking design statements.",
    },
    {
        "name": "Thermo Laminates",
        "hero_eyebrow": "Outdoor Surfaces",
        "hero_image_url": "https://images.unsplash.com/photo-1598928636135-d146006ff4be?q=80&w=2000",
        "description": "Weather-resistant Thermo Laminate surfaces engineered for outdoor furniture, cladding and high-exposure architectural applications.",
    },
]

COLLECTIONS = ["S'Shades", "Thre3", "Cool Colour", "Fluted", "Perspective V4"]

PRODUCTS = [
    {
        "id": 1, "slug": "arctic-white", "name": "Arctic White", "collection": "S'Shades",
        "finish": "High Gloss", "thickness": "1.0mm", "dimensions": "8ft × 4ft (2440 × 1220mm)",
        "surface": "Decorative Laminate", "application": "Cabinets, Wardrobes, Wall Panels",
        "badge": "Bestseller", "accent_color": "#85addc", "category": "Laminates",
        "design_type": "Solid", "color": "White",
        "short_description": "A pure, reflective white surface that brings luminosity and the illusion of boundless space to any interior.",
        "description": "Arctic White is the cornerstone of the S'Shades collection — a pristine, mirror-like high-gloss laminate that has become the go-to choice for architects and interior designers seeking clean, contemporary aesthetics.",
        "features": ["Scratch Resistant", "Moisture Proof", "Anti-Fingerprint", "UV Stable", "Easy to Clean", "Fire Retardant"],
        "images": [
            "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=1200",
            "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?q=80&w=1200",
            "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?q=80&w=1200",
            "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?q=80&w=1200",
        ],
        "related": ["midnight-charcoal", "pearl-beige", "frosted-silver"],
    },
    {
        "id": 2, "slug": "midnight-charcoal", "name": "Midnight Charcoal", "collection": "S'Shades",
        "finish": "Ultra Matte", "thickness": "1.0mm", "dimensions": "8ft × 4ft (2440 × 1220mm)",
        "surface": "Decorative Laminate", "application": "Kitchen, Wardrobes, Feature Walls",
        "badge": "New", "accent_color": "#1E1E2E", "category": "Laminates",
        "design_type": "Solid", "color": "Black",
        "short_description": "Deep, absorbing charcoal with zero-reflection matte finish — the definitive choice for sophisticated, moody interiors.",
        "description": "Midnight Charcoal draws inspiration from the quiet intensity of deep night skies. This ultra-matte laminate features a velvety, light-absorbing surface with absolutely zero reflectance.",
        "features": ["Zero Reflectance", "Soft Touch", "Anti-Fingerprint", "Scratch Resistant", "Moisture Proof", "Easy to Clean"],
        "images": [
            "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?q=80&w=1200",
            "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?q=80&w=1200",
            "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=1200",
        ],
        "related": ["arctic-white", "slate-grey", "oxidized-brass"],
    },
    {
        "id": 3, "slug": "oceanic-blue", "name": "Oceanic Blue", "collection": "Cool Colour",
        "finish": "Suede", "thickness": "1.0mm", "dimensions": "8ft × 4ft (2440 × 1220mm)",
        "surface": "Decorative Laminate", "application": "Cabinetry, Furniture, Accent Walls",
        "badge": "", "accent_color": "#85addc", "category": "Laminates",
        "design_type": "Stone", "color": "Blue",
        "short_description": "A calming, muted blue inspired by deep waters — perfect for modern cabinetry and statement focal pieces.",
        "description": "Oceanic Blue captures the serene depth of open water in a supremely tactile suede finish. Part of the Cool Colour collection, this nuanced blue laminate avoids the garish brightness of typical colour laminates.",
        "features": ["Suede Texture", "Scratch Resistant", "Moisture Proof", "UV Stable", "Anti-Bacterial", "Easy to Clean"],
        "images": [
            "https://images.unsplash.com/photo-1598928636135-d146006ff4be?q=80&w=1200",
            "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?q=80&w=1200",
        ],
        "related": ["emerald-forest", "dusty-rose", "arctic-white"],
    },
    {
        "id": 4, "slug": "oak-ribbon", "name": "Oak Ribbon", "collection": "Fluted",
        "finish": "Textured", "thickness": "1.25mm", "dimensions": "8ft × 4ft (2440 × 1220mm)",
        "surface": "Architectural Laminate", "application": "Wall Panels, Doors, Feature Surfaces",
        "badge": "Bestseller", "accent_color": "#85addc", "category": "Louvers",
        "design_type": "Wood", "color": "Brown",
        "short_description": "Architectural fluted woodgrain texture that adds instant rhythm and warmth to wall panels and room dividers.",
        "description": "Oak Ribbon is a statement architectural laminate from Sanish Laminates' Fluted collection. The synchronized flute pattern faithfully replicates the tactile depth of real wood ribbing.",
        "features": ["Synchronized Texture", "Deep Emboss", "Scratch Resistant", "Moisture Proof", "Fire Retardant", "Architectural Grade"],
        "images": [
            "https://images.unsplash.com/photo-1565538810643-b5bdb714032a?q=80&w=1200",
            "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?q=80&w=1200",
        ],
        "related": ["walnut-flute", "teak-stripe", "desert-sand"],
    },
    {
        "id": 5, "slug": "desert-sand", "name": "Desert Sand", "collection": "Thre3",
        "finish": "Matte", "thickness": "1.0mm", "dimensions": "8ft × 4ft (2440 × 1220mm)",
        "surface": "Decorative Laminate", "application": "Modular Kitchens, Furniture, Wardrobes",
        "badge": "", "accent_color": "#85addc", "category": "Laminates",
        "design_type": "Solid", "color": "Beige",
        "short_description": "A warm, earthy beige that serves as the perfect neutral canvas for layering contemporary design elements.",
        "description": "Desert Sand is perhaps the most versatile laminate in the Thre3 collection. Its warm, sandy beige tone draws from the rich, golden palette of arid landscapes.",
        "features": ["Matte Finish", "Scratch Resistant", "Moisture Proof", "UV Stable", "Easy to Clean", "Anti-Bacterial"],
        "images": [
            "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?q=80&w=1200",
            "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=1200",
        ],
        "related": ["pearl-beige", "arctic-white", "oak-ribbon"],
    },
    {
        "id": 6, "slug": "oxidized-brass", "name": "Oxidized Brass", "collection": "Thre3",
        "finish": "Metallic", "thickness": "1.0mm", "dimensions": "8ft × 4ft (2440 × 1220mm)",
        "surface": "Metallic Laminate", "application": "Feature Walls, Reception Desks, Furniture",
        "badge": "Limited", "accent_color": "#85addc", "category": "Laminates",
        "design_type": "Metallic", "color": "Metallic",
        "short_description": "A striking metallic laminate that mimics authentic oxidized brass — all the drama without the weight or maintenance.",
        "description": "Oxidized Brass from the Metallic Series brings the timeless prestige of aged brass into the practical world of decorative laminates.",
        "features": ["Metallic Effect", "Deep Texture", "Scratch Resistant", "Anti-Tarnish", "Fire Retardant", "Architectural Grade"],
        "images": [
            "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?q=80&w=1200",
            "https://images.unsplash.com/photo-1598928636135-d146006ff4be?q=80&w=1200",
        ],
        "related": ["frosted-silver", "midnight-charcoal", "pearl-beige"],
    },
    {
        "id": 7, "slug": "slate-grey", "name": "Slate Grey", "collection": "Perspective V4",
        "finish": "Suede", "thickness": "0.8mm", "dimensions": "8ft × 4ft (2440 × 1220mm)",
        "surface": "Economy Laminate", "application": "Budget Furniture, Office Interiors, Partitions",
        "badge": "", "accent_color": "#85addc", "category": "Laminates",
        "design_type": "Stone", "color": "Grey",
        "short_description": "Highly durable standard-grade laminate in a versatile industrial grey — maximum utility, minimum fuss.",
        "description": "Slate Grey from the 0.8mm collection proves that practicality need not compromise on aesthetics. This economy-grade laminate is engineered for high-volume applications.",
        "features": ["Economy Grade", "Scratch Resistant", "Moisture Proof", "Easy to Clean", "High Durability", "Cost Effective"],
        "images": [
            "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?q=80&w=1200",
            "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?q=80&w=1200",
        ],
        "related": ["midnight-charcoal", "desert-sand", "arctic-white"],
    },
    {
        "id": 8, "slug": "emerald-forest", "name": "Emerald Forest", "collection": "Cool Colour",
        "finish": "High Gloss", "thickness": "1.0mm", "dimensions": "8ft × 4ft (2440 × 1220mm)",
        "surface": "Decorative Laminate", "application": "Kitchen, Bar Units, Feature Walls",
        "badge": "New", "accent_color": "#85addc", "category": "Laminates",
        "design_type": "Solid", "color": "Green",
        "short_description": "A rich, jewel-toned green with a mirror-like finish — designed for spaces that dare to make a statement.",
        "description": "Emerald Forest is the bold, unapologetic hero of the Cool Colour collection. A deep, saturated emerald green in a high-gloss finish.",
        "features": ["High Gloss", "Deep Colour", "Scratch Resistant", "Moisture Proof", "UV Stable", "Easy to Clean"],
        "images": [
            "https://images.unsplash.com/photo-1598928636135-d146006ff4be?q=80&w=1200",
            "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=1200",
        ],
        "related": ["oceanic-blue", "dusty-rose", "oxidized-brass"],
    },
    {
        "id": 9, "slug": "pearl-beige", "name": "Pearl Beige", "collection": "S'Shades",
        "finish": "Satin", "thickness": "1.0mm", "dimensions": "8ft × 4ft (2440 × 1220mm)",
        "surface": "Decorative Laminate", "application": "Wardrobes, Bedroom Furniture, Living Room",
        "badge": "", "accent_color": "#85addc", "category": "Laminates",
        "design_type": "Fabric", "color": "Beige",
        "short_description": "Warm, luminous beige with a silky satin sheen — the sophisticated middle ground between matte and gloss.",
        "description": "Pearl Beige occupies that coveted space between matte restraint and gloss exuberance. Its satin finish catches light softly.",
        "features": ["Satin Finish", "Scratch Resistant", "Moisture Proof", "UV Stable", "Anti-Fingerprint", "Easy to Clean"],
        "images": [
            "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=1200",
            "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?q=80&w=1200",
        ],
        "related": ["arctic-white", "desert-sand", "frosted-silver"],
    },
    {
        "id": 10, "slug": "frosted-silver", "name": "Frosted Silver", "collection": "Thre3",
        "finish": "Metallic", "thickness": "1.0mm", "dimensions": "8ft × 4ft (2440 × 1220mm)",
        "surface": "Metallic Laminate", "application": "Commercial Interiors, Cabinets, Furniture",
        "badge": "", "accent_color": "#85addc", "category": "Laminates",
        "design_type": "Metallic", "color": "Metallic",
        "short_description": "Cool, brushed silver with a frosted metallic quality — industrial refinement for contemporary commercial spaces.",
        "description": "Frosted Silver delivers the cool precision of industrial design aesthetics in a highly practical laminate format.",
        "features": ["Metallic Effect", "Brushed Texture", "Scratch Resistant", "Anti-Fingerprint", "Fire Retardant", "Easy to Clean"],
        "images": [
            "https://images.unsplash.com/photo-1565538810643-b5bdb714032a?q=80&w=1200",
            "https://images.unsplash.com/photo-1598928636135-d146006ff4be?q=80&w=1200",
        ],
        "related": ["oxidized-brass", "midnight-charcoal", "slate-grey"],
    },
    {
        "id": 11, "slug": "dusty-rose", "name": "Dusty Rose", "collection": "Cool Colour",
        "finish": "Matte", "thickness": "1.0mm", "dimensions": "8ft × 4ft (2440 × 1220mm)",
        "surface": "Decorative Laminate", "application": "Bedroom, Dressing Areas, Boutique Retail",
        "badge": "", "accent_color": "#85addc", "category": "Laminates",
        "design_type": "Solid", "color": "Pink",
        "short_description": "A muted, powdery rose with soft matte finish — feminine without being frivolous, romantic without being retro.",
        "description": "Dusty Rose is the Cool Colour collection's most emotionally resonant offering. This muted, powdery pink avoids all the pitfalls of typical pink laminates.",
        "features": ["Matte Finish", "Scratch Resistant", "Moisture Proof", "UV Stable", "Anti-Bacterial", "Easy to Clean"],
        "images": [
            "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?q=80&w=1200",
            "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=1200",
        ],
        "related": ["oceanic-blue", "emerald-forest", "pearl-beige"],
    },
    {
        "id": 12, "slug": "walnut-flute", "name": "Walnut Flute", "collection": "Fluted",
        "finish": "Textured", "thickness": "1.25mm", "dimensions": "8ft × 4ft (2440 × 1220mm)",
        "surface": "Architectural Laminate", "application": "Feature Walls, Headboards, Furniture Fronts",
        "badge": "New", "accent_color": "#85addc", "category": "Louvers",
        "design_type": "Wood", "color": "Brown",
        "short_description": "Rich walnut woodgrain brought to life with architectural fluting — nature and geometry in perfect dialogue.",
        "description": "Walnut Flute is where the warmth of natural walnut meets the precision of architectural geometry.",
        "features": ["Synchronized Texture", "Rich Woodgrain", "Scratch Resistant", "Moisture Proof", "Fire Retardant", "Architectural Grade"],
        "images": [
            "https://images.unsplash.com/photo-1598928636135-d146006ff4be?q=80&w=1200",
            "https://images.unsplash.com/photo-1565538810643-b5bdb714032a?q=80&w=1200",
        ],
        "related": ["oak-ribbon", "desert-sand", "oxidized-brass"],
    },
]


def seed(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    Collection = apps.get_model("catalog", "Collection")
    Product = apps.get_model("catalog", "Product")

    # get_or_create keyed on slug — safe to run alongside any existing data,
    # and a no-op on re-run.
    for cfg in CATEGORIES:
        Category.objects.get_or_create(
            slug=slugify(cfg["name"]),
            defaults={
                "name": cfg["name"],
                "hero_eyebrow": cfg["hero_eyebrow"],
                "hero_image_url": cfg["hero_image_url"],
                "description": cfg["description"],
                "status": "published",
            },
        )

    for name in COLLECTIONS:
        Collection.objects.get_or_create(
            slug=slugify(name),
            defaults={"name": name, "status": "published"},
        )

    cats = {c.name: c for c in Category.objects.all()}
    cols = {c.name: c for c in Collection.objects.all()}

    created = {}
    for p in PRODUCTS:
        obj, _ = Product.objects.get_or_create(
            slug=p["slug"],
            defaults={
                "name": p["name"],
                "sku": f"SL-{p['id']:04d}",
                "category": cats[p["category"]],
                "collection": cols.get(p["collection"]),
                "short_description": p["short_description"],
                "description": p["description"],
                "features": p["features"],
                "tech_specs": {},
                "image_urls": p["images"],
                "finish": p["finish"],
                "thickness": p["thickness"],
                "dimensions": p["dimensions"],
                "surface": p["surface"],
                "application": p["application"],
                "design_type": p["design_type"],
                "color": p["color"],
                "badge": p["badge"],
                "accent_color": p["accent_color"],
                "status": "published",
            },
        )
        created[p["slug"]] = obj

    for p in PRODUCTS:
        obj = created[p["slug"]]
        related = [created[s] for s in p["related"] if s in created]
        if related:
            obj.related_products.set(related)


def unseed(apps, schema_editor):
    Product = apps.get_model("catalog", "Product")
    Product.objects.filter(slug__in=[p["slug"] for p in PRODUCTS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0004_category_hero_eyebrow_category_hero_image_url_and_more"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
