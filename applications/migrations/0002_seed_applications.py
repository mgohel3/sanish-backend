"""Seed ApplicationCategory / ApplicationProject with the current live data
from the frontend's `src/lib/applications.ts`, so the CMS starts out with
real, editable content instead of empty tables. Nothing on the public site
changes until the frontend is wired to read from the API (a following step).
"""
from django.db import migrations


CATEGORIES = [
    {
        "slug": "kitchens", "label": "Kitchens",
        "description": "From high-gloss island units to soft-touch matte cabinetry, see how Sanish surfaces bring durability and design to the heart of the home.",
        "accent": "#f39ba2",
        "image": "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?q=80&w=1400",
    },
    {
        "slug": "commercial", "label": "Commercial",
        "description": "Offices, co-working studios and workplaces finished in laminates built for daily wear, glare-free surfaces, and brand-aligned interiors.",
        "accent": "#85addc",
        "image": "https://images.unsplash.com/photo-1618220179428-22790b461013?q=80&w=1400",
    },
    {
        "slug": "retail", "label": "Retail",
        "description": "Boutiques and showrooms where surface finish sets the tone — dramatic gloss, warm texture, and statement cladding.",
        "accent": "#fabf7d",
        "image": "https://images.unsplash.com/photo-1598928506311-c55ded91a20c?q=80&w=1400",
    },
    {
        "slug": "hospitality", "label": "Hospitality",
        "description": "Hotels and restaurants finished in Sanish laminates for warm, textured atmospheres that balance daily durability with hospitality-grade elegance.",
        "accent": "#d4a574",
        "image": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=1400",
    },
    {
        "slug": "residential", "label": "Residential",
        "description": "Living rooms, bedrooms and wardrobes finished with Sanish laminates for a look that feels tactile, timeless and made to last.",
        "accent": "#ac8cc0",
        "image": "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?q=80&w=1400",
    },
]

# (slug, label, category_slug, finish, image, tall, description, location, year, designer, area, products, gallery, highlights)
PROJECTS = [
    ("modern-kitchen-gloss", "Modern Kitchen", "kitchens", "High Gloss White",
     "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?q=80&w=1400", False,
     "A complete kitchen transformation for a family home in Delhi NCR. The brief called for a clean, contemporary aesthetic that felt premium yet liveable. Sanish High Gloss White laminates on the cabinet fronts reflect natural light beautifully, making the relatively compact kitchen feel expansive and airy.",
     "Delhi NCR, India", "2025", "Studio Forma", "320 sq ft",
     [
         {"name": "S'Shades Pearl White", "code": "High Gloss 1.0mm - 3001 HG", "collection": "S'Shades", "finish": "High Gloss", "usage": "Upper and lower cabinet shutters", "product_slug": "sshades-pearl-white"},
         {"name": "Cool Colour Linen Grey", "code": "Ultra Matte 0.8mm - 3002 UM", "collection": "Cool Colour", "finish": "Ultra Matte", "usage": "Island countertop fascia and open shelving", "product_slug": "cool-colour-linen-grey"},
     ],
     ["https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?q=80&w=1400", "https://images.unsplash.com/photo-1600566753376-12c8ab7fb75b?q=80&w=1400", "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?q=80&w=900"],
     ["Light-reflective High Gloss finish", "Scratch & moisture resistant", "Delivered in 3 working days"]),

    ("retail-space-stone", "Retail Space", "retail", "Textured Stone",
     "https://images.unsplash.com/photo-1598928506311-c55ded91a20c?q=80&w=1400", True,
     "A luxury fragrance boutique in a high-footfall mall required wall cladding that conveyed heritage and sophistication. The Textured Stone laminate from Thre3 was selected for its natural mineral depth — it anchors the space and provides a dramatic backdrop for the product display.",
     "Select Citywalk, New Delhi", "2025", "Axis Design Co.", "650 sq ft",
     [
         {"name": "Thre3 Slate Noir", "code": "Textured Stone 1.0mm - 3003 TS", "collection": "Thre3", "finish": "Textured Stone", "usage": "Feature wall behind display shelves and cash counter", "product_slug": "thre3-slate-noir"},
         {"name": "S'Shades Warm White", "code": "Matte 1.0mm - 3004 MT", "collection": "S'Shades", "finish": "Matte", "usage": "Ceiling coves and side wall panels", "product_slug": "sshades-warm-white"},
     ],
     ["https://images.unsplash.com/photo-1555041469-a586c61ea9bc?q=80&w=1400", "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?q=80&w=900", "https://images.unsplash.com/photo-1604014237800-1c9102c219da?q=80&w=1400"],
     ["IS:848 fire-retardant grade", "Anti-scuff coating", "Custom cut-to-size panels"]),

    ("corporate-office-matte", "Corporate Office", "commercial", "Ultra Matte",
     "https://images.unsplash.com/photo-1618220179428-22790b461013?q=80&w=1400", False,
     "A 4,000 sq ft co-working office for a fintech startup required a palette that felt calm and focused without being sterile. Ultra Matte laminates in warm charcoal and off-white tones were used across workstation dividers, reception cladding, and break-room cabinetry — achieving a cohesive, brand-aligned environment.",
     "Bangalore, Karnataka", "2024", "Workhaus Studio", "4,000 sq ft",
     [
         {"name": "Cool Colour Charcoal", "code": "Ultra Matte 0.8mm - 3005 UM", "collection": "Cool Colour", "finish": "Ultra Matte", "usage": "Workstation panel cladding and reception desk", "product_slug": "cool-colour-charcoal"},
         {"name": "0.8mm Warm White", "code": "Matte 0.8mm - 3006 MT", "collection": "Perspective V4", "finish": "Matte", "usage": "Break-room cabinets and storage walls", "product_slug": "08mm-warm-white"},
     ],
     ["https://images.unsplash.com/photo-1497366216548-37526070297c?q=80&w=1400", "https://images.unsplash.com/photo-1497366216548-37526070297c?q=80&w=900", "https://images.unsplash.com/photo-1618220179428-22790b461013?q=80&w=900"],
     ["Anti-fingerprint Ultra Matte surface", "Glare-free for screen-heavy workspaces", "Full office fit-out in 6 days"]),

    ("luxury-living-room", "Luxury Living Room", "residential", "Acrylic Pearl",
     "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?q=80&w=1400", False,
     "A high-net-worth residential project in Mumbai's Juhu neighbourhood called for a living room that exuded understated luxury. The TV unit and display wall use S'Shades Acrylic Pearl — its luminous, slightly reflective surface catches the evening light and creates a jewel-like focal point without overwhelming the room.",
     "Juhu, Mumbai", "2025", "De Sousa Hughes", "800 sq ft",
     [
         {"name": "S'Shades Acrylic Pearl", "code": "High Gloss 1.0mm - 3007 HG", "collection": "S'Shades", "finish": "High Gloss", "usage": "TV unit shutters and display wall niches", "product_slug": "sshades-acrylic-pearl"},
         {"name": "Thre3 Warm Linen", "code": "Suede 1.0mm - 3008 SU", "collection": "Thre3", "finish": "Suede", "usage": "Sofa backdrop wall cladding", "product_slug": "thre3-warm-linen"},
     ],
     ["https://images.unsplash.com/photo-1583847268964-b28dc8f51f92?q=80&w=1400", "https://images.unsplash.com/photo-1600566753376-12c8ab7fb75b?q=80&w=1400", "https://images.unsplash.com/photo-1604014237800-1c9102c219da?q=80&w=900"],
     ["Depth and luminosity from 1mm thickness", "UV stable — no yellowing over time", "Paired with brass inlay detailing"]),

    ("boutique-hotel-metallic", "Boutique Hotel", "hospitality", "Metallic Bronze",
     "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=1400", True,
     "A 22-room boutique hotel in Jaipur's heritage zone needed interiors that honoured the city's artisan tradition while appealing to international travellers. Metallic Bronze laminates were specified for corridor accent walls and room headboard panels, creating a warm, gilded atmosphere that complements the property's hand-blocked textile collection.",
     "Jaipur, Rajasthan", "2024", "Studio Aapro", "12,000 sq ft",
     [
         {"name": "S'Shades Oxidised Brass", "code": "Metallic 1.0mm - 3009 ME", "collection": "S'Shades", "finish": "Metallic", "usage": "Corridor accent wall panels and headboards", "product_slug": "oxidized-brass"},
         {"name": "Thre3 Terracotta Matte", "code": "Matte 1.0mm - 3010 MT", "collection": "Thre3", "finish": "Matte", "usage": "Wardrobe and minibar unit fronts", "product_slug": "thre3-terracotta"},
     ],
     ["https://images.unsplash.com/photo-1582131503261-fca1d1c0589f?q=80&w=1400", "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?q=80&w=1400", "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=900"],
     ["Fire-retardant IS:848 certified", "Anti-tarnish metallic coating", "Custom 22-room specification"]),

    ("premium-kitchen-suede", "Premium Kitchen", "kitchens", "Suede Greige",
     "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?q=80&w=1400", False,
     "A villa kitchen in Hyderabad's Jubilee Hills required a palette that could bridge a warm, earthy aesthetic with modern European appliances. Suede Greige from the Thre3 collection provided the ideal muted tone — natural-feeling to the touch, highly practical in a busy cooking environment, and compatible with brushed stainless hardware.",
     "Jubilee Hills, Hyderabad", "2025", "Patel & Rao Interiors", "450 sq ft",
     [
         {"name": "Thre3 Suede Greige", "code": "Suede 1.0mm - 3011 SU", "collection": "Thre3", "finish": "Suede", "usage": "All cabinet fronts, including pantry unit", "product_slug": "thre3-suede-greige"},
         {"name": "0.8mm Pale Sage", "code": "Matte 0.8mm - 3012 MT", "collection": "Perspective V4", "finish": "Matte", "usage": "Island base fascia and overhead storage", "product_slug": "08mm-pale-sage"},
     ],
     ["https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?q=80&w=1400", "https://images.unsplash.com/photo-1600566753376-12c8ab7fb75b?q=80&w=900", "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?q=80&w=900"],
     ["Soft-touch Suede texture", "Steam and humidity resistant", "Seamless colour match across 68 shutters"]),

    ("coastal-kitchen-matte", "Coastal Kitchen", "kitchens", "Sea Salt Matte",
     "https://images.unsplash.com/photo-1600566753376-12c8ab7fb75b?q=80&w=1400", False,
     "A holiday home kitchen in Goa called for a breezy, coastal palette that could stand up to humidity and salt air. Sea Salt Matte laminates on the cabinetry bring a soft, weathered-wood look without any of the maintenance real timber would demand this close to the coast.",
     "Candolim, Goa", "2025", "Coastline Interiors", "280 sq ft",
     [
         {"name": "0.8mm Pale Sage", "code": "Matte 0.8mm - 3013 MT", "collection": "Perspective V4", "finish": "Matte", "usage": "Base cabinet shutters and open shelving", "product_slug": "08mm-pale-sage"},
         {"name": "S'Shades Warm White", "code": "Matte 1.0mm - 3014 MT", "collection": "S'Shades", "finish": "Matte", "usage": "Upper cabinets and window seat panelling", "product_slug": "sshades-warm-white"},
     ],
     ["https://images.unsplash.com/photo-1600566753376-12c8ab7fb75b?q=80&w=1400", "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?q=80&w=900", "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?q=80&w=900"],
     ["Humidity and salt-air resistant", "Soft coastal colour palette", "Low-maintenance matte surface"]),

    ("minimalist-kitchen-loft", "Minimalist Loft Kitchen", "kitchens", "Concrete Grey Textured",
     "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?q=80&w=1400", False,
     "An industrial loft conversion in Mumbai's Lower Parel called for a kitchen that felt at home against exposed brick and steel beams. Concrete Grey Textured laminates on a handle-less cabinet run keep the look pared-back and architectural.",
     "Lower Parel, Mumbai", "2024", "Grey Matter Studio", "210 sq ft",
     [
         {"name": "0.8mm Concrete Grey", "code": "Textured 0.8mm - 3015 TX", "collection": "Perspective V4", "finish": "Textured", "usage": "Handle-less base and wall cabinet shutters", "product_slug": "08mm-concrete"},
         {"name": "Cool Colour Charcoal", "code": "Ultra Matte 0.8mm - 3016 UM", "collection": "Cool Colour", "finish": "Ultra Matte", "usage": "Kitchen peninsula and breakfast counter fascia", "product_slug": "cool-colour-charcoal"},
     ],
     ["https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?q=80&w=1400", "https://images.unsplash.com/photo-1600566753376-12c8ab7fb75b?q=80&w=900", "https://images.unsplash.com/photo-1618220179428-22790b461013?q=80&w=900"],
     ["Handle-less minimalist profile", "Pairs with exposed brick and steel", "Textured surface hides daily fingerprints"]),

    ("showroom-display", "Showroom Display", "retail", "High Gloss Anthracite",
     "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?q=80&w=1400", False,
     "A luxury automobile accessories showroom in Pune required display plinths and wall backdrops that let the product take centre stage. High Gloss Anthracite laminates deliver a dramatic, gallery-like backdrop while the reflective surface doubles the visual impact of the displayed merchandise.",
     "Koregaon Park, Pune", "2024", "Praxis Design Studio", "900 sq ft",
     [
         {"name": "S'Shades Anthracite Gloss", "code": "High Gloss 1.0mm - 3017 HG", "collection": "S'Shades", "finish": "High Gloss", "usage": "Feature wall, display plinths, and reception counter", "product_slug": "sshades-anthracite"},
         {"name": "Cool Colour Arctic White", "code": "Ultra Matte 0.8mm - 3018 UM", "collection": "Cool Colour", "finish": "Ultra Matte", "usage": "Ceiling and secondary wall panels", "product_slug": "cool-colour-arctic"},
     ],
     ["https://images.unsplash.com/photo-1598928506311-c55ded91a20c?q=80&w=1400", "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?q=80&w=900", "https://images.unsplash.com/photo-1618220179428-22790b461013?q=80&w=900"],
     ["Mirror-like reflective surface", "Dust and smudge repellent coating", "Installed in a single weekend"]),

    ("open-plan-office", "Open Plan Office", "commercial", "Woodgrain Walnut",
     "https://images.unsplash.com/photo-1497366216548-37526070297c?q=80&w=1400", False,
     "A media agency in Chennai's Nungambakkam district wanted an open-plan studio that balanced creative energy with warmth. Woodgrain Walnut laminates on the acoustic partition panels and library wall add organic texture to an otherwise industrial space with polished concrete floors and exposed ducting.",
     "Nungambakkam, Chennai", "2024", "Collective Works", "2,800 sq ft",
     [
         {"name": "Thre3 Walnut Natural", "code": "Textured 1.0mm - 3019 TX", "collection": "Thre3", "finish": "Textured", "usage": "Acoustic partition panels and library wall feature", "product_slug": "thre3-walnut"},
         {"name": "Cool Colour Slate Grey", "code": "Matte 0.8mm - 3020 MT", "collection": "Cool Colour", "finish": "Matte", "usage": "Modular workstation surfaces", "product_slug": "cool-colour-slate"},
     ],
     ["https://images.unsplash.com/photo-1618220179428-22790b461013?q=80&w=1400", "https://images.unsplash.com/photo-1497366216548-37526070297c?q=80&w=900", "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=900"],
     ["Wood texture without the maintenance", "Abrasion class AC4 rated", "6,000 sq ft of panels specified"]),

    ("master-bedroom-linen", "Master Bedroom", "residential", "Soft Linen Matte",
     "https://images.unsplash.com/photo-1583847268964-b28dc8f51f92?q=80&w=1400", True,
     "A penthouse master bedroom in Gurugram's Golf Course Road required wardrobe and headboard finishes that felt calm, tactile, and timeless. Soft Linen Matte from the Cool Colour range was specified for the full-height wardrobe wall. Its chalky, breathable appearance complements the custom upholstered bed and the natural light from floor-to-ceiling windows.",
     "Golf Course Road, Gurugram", "2025", "Saakaar Collective", "600 sq ft",
     [
         {"name": "Cool Colour Soft Linen", "code": "Matte 0.8mm - 3021 MT", "collection": "Cool Colour", "finish": "Matte", "usage": "Full-height 14-door wardrobe", "product_slug": "cool-colour-soft-linen"},
         {"name": "S'Shades Ivory Satin", "code": "Satin 1.0mm - 3022 ST", "collection": "S'Shades", "finish": "Satin", "usage": "Bed headboard panel and side units", "product_slug": "sshades-ivory-satin"},
     ],
     ["https://images.unsplash.com/photo-1604014237800-1c9102c219da?q=80&w=1400", "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?q=80&w=900", "https://images.unsplash.com/photo-1583847268964-b28dc8f51f92?q=80&w=900"],
     ["Zero-glare matte surface", "14-door bespoke wardrobe", "Paired with PU lacquer interior linings"]),

    ("island-kitchen-calacatta", "Island Kitchen", "kitchens", "Calacatta Gloss",
     "https://images.unsplash.com/photo-1600566753376-12c8ab7fb75b?q=80&w=1400", False,
     "An architect's own residence in Ahmedabad's Satellite neighbourhood served as the testing ground for a bold kitchen concept. Calacatta Gloss laminates — with their bold marble-like veining — were used on the island and upper cabinet faces, creating a dramatic tension with the raw concrete ceiling and industrial pendant lighting.",
     "Satellite, Ahmedabad", "2025", "Bimal Shah Architects", "380 sq ft",
     [
         {"name": "Thre3 Calacatta Oro", "code": "High Gloss 1.0mm - 3023 HG", "collection": "Thre3", "finish": "High Gloss", "usage": "Kitchen island faces and upper cabinet shutters", "product_slug": "thre3-calacatta"},
         {"name": "0.8mm Concrete Grey", "code": "Textured 0.8mm - 3024 TX", "collection": "Perspective V4", "finish": "Textured", "usage": "Lower cabinet unit base", "product_slug": "08mm-concrete"},
     ],
     ["https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?q=80&w=1400", "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?q=80&w=1400", "https://images.unsplash.com/photo-1600566753376-12c8ab7fb75b?q=80&w=900"],
     ["Stone look without stone weight", "Easy to clean gloss surface", "Featured in Architectural Digest India"]),

    ("restaurant-interior-fluted", "Restaurant Interior", "hospitality", "Fluted Oak",
     "https://images.unsplash.com/photo-1582131503261-fca1d1c0589f?q=80&w=1400", False,
     "A 60-cover farm-to-table restaurant in Bengaluru's Indiranagar used Sanish Fluted laminates to create a warm, textured dining environment that references artisan woodwork without the cost or fragility of real timber. The vertical fluting draws the eye upward, making the compact space feel taller.",
     "Indiranagar, Bengaluru", "2024", "The Third Row Studio", "1,800 sq ft",
     [
         {"name": "Fluted Oak Natural", "code": "Textured 3.0mm - 3025 TX", "collection": "Fluted", "finish": "Textured", "usage": "Perimeter wall panels, bar back, and column cladding", "product_slug": "fluted-oak-natural"},
         {"name": "Thre3 Burnt Umber", "code": "Matte 1.0mm - 3026 MT", "collection": "Thre3", "finish": "Matte", "usage": "Banquette seating panels and host stand", "product_slug": "thre3-burnt-umber"},
     ],
     ["https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=1400", "https://images.unsplash.com/photo-1582131503261-fca1d1c0589f?q=80&w=900", "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?q=80&w=900"],
     ["3D fluted profile adds depth", "Food-safe wipe-clean surface", "60-cover install completed in 4 days"]),

    ("wardrobe-pure-white", "Wardrobe & Closet", "residential", "Pure White Matte",
     "https://images.unsplash.com/photo-1604014237800-1c9102c219da?q=80&w=1400", False,
     "A children's bedroom in a Kolkata townhouse was designed around a full-wall wardrobe system using Pure White Matte laminates. The brief prioritised a timeless, adaptable finish that could grow with the child — bright enough to reflect light in the north-facing room, while being forgiving of the inevitable marks and knocks of daily use.",
     "Ballygunge, Kolkata", "2025", "Saha & Partners", "220 sq ft",
     [
         {"name": "Cool Colour Pure White", "code": "Ultra Matte 0.8mm - 3027 UM", "collection": "Cool Colour", "finish": "Ultra Matte", "usage": "All wardrobe shutter and drawer fronts", "product_slug": "cool-colour-pure-white"},
         {"name": "0.8mm Blush Pink", "code": "Satin 0.8mm - 3028 ST", "collection": "Perspective V4", "finish": "Satin", "usage": "Study desk and open shelf inserts", "product_slug": "08mm-blush-pink"},
     ],
     ["https://images.unsplash.com/photo-1583847268964-b28dc8f51f92?q=80&w=1400", "https://images.unsplash.com/photo-1604014237800-1c9102c219da?q=80&w=900", "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?q=80&w=900"],
     ["Scratch-resistant for children's rooms", "Non-toxic, formaldehyde-free", "White stays white — UV stable"]),
]


def seed(apps, schema_editor):
    ApplicationCategory = apps.get_model("applications", "ApplicationCategory")
    ApplicationProject = apps.get_model("applications", "ApplicationProject")

    cats_by_slug = {}
    for i, c in enumerate(CATEGORIES):
        cat, _ = ApplicationCategory.objects.get_or_create(
            slug=c["slug"],
            defaults={
                "label": c["label"], "description": c["description"],
                "accent": c["accent"], "image": c["image"], "position": i,
            },
        )
        cats_by_slug[c["slug"]] = cat

    for i, (slug, label, cat_slug, finish, image, tall, description, location, year,
            designer, area, products, gallery, highlights) in enumerate(PROJECTS):
        if ApplicationProject.objects.filter(slug=slug).exists():
            continue
        ApplicationProject.objects.create(
            slug=slug, label=label, category=cats_by_slug[cat_slug], finish=finish,
            image=image, tall=tall, description=description, location=location,
            year=year, designer=designer or "", area=area or "",
            gallery=[{"image": g} for g in gallery],
            highlights=[{"text": h} for h in highlights],
            products=products,
            position=i,
        )


def unseed(apps, schema_editor):
    ApplicationCategory = apps.get_model("applications", "ApplicationCategory")
    ApplicationCategory.objects.filter(
        slug__in=[c["slug"] for c in CATEGORIES]
    ).delete()  # cascades to projects


class Migration(migrations.Migration):

    dependencies = [
        ("applications", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
