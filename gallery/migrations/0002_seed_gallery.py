"""Import every image that already exists in
``sanish-next-fixed/public/assets/img/gallery/<slug>/`` (346 files across 5
catalogues, per ``src/generated/gallery-manifest.json`` at the time this was
written) as real, CMS-manageable rows pointing at their existing file paths.

Nothing is moved, re-uploaded, or deleted — the frontend keeps serving the
exact same static files. This just gives the CMS visibility into content
that was previously only manageable by dropping files into a server folder.
"""
import re

from django.db import migrations

# Mirrors CATALOGUE_NAMES / CATALOGUE_ORDER in sanish-next-fixed's src/lib/gallery.ts
CATALOGUE_LABELS = {
    "sshades": "S'Shades",
    "thre3": "Thre3",
    "cool-colour": "Cool Colour",
    "08mm": "Perspective V4",
    "thermo": "Thermo Laminates",
}

# Display order the live site actually uses (CATALOGUE_ORDER in gallery.ts) —
# NOT the manifest's alphabetical folder order, so `position` here must match
# this, not the order MANIFEST entries happen to appear in below.
CATALOGUE_ORDER = ["sshades", "thre3", "cool-colour", "08mm", "thermo"]

# Exact contents of src/generated/gallery-manifest.json at time of writing.
MANIFEST = [
    {"slug": "08mm", "files": [
        "6001_PW.jpg", "6012_PW.jpg", "6014_PW.jpg", "6015_PW.jpg", "6021_PW.jpg",
        "6030_PW.jpg", "6031_PW.jpg", "6032_PW.jpg", "6050_PW.jpg", "6053_PW.jpg",
        "6055_PW.jpg", "6057_PW.jpg", "6059_PW.jpg", "6065_PW.jpg", "6068_PW.jpg",
        "6070_PW.jpg", "6075_PW.jpg", "6086 _PW.jpg", "6091_PW.jpg", "6095_PW.jpg",
        "6099_PW.jpg", "6101_PW.jpg", "6102_PW.jpg", "6103_PW.jpg", "6104_PW.jpg",
        "6105_PW.jpg", "6106_PW.jpg", "6151_PW.jpg", "6153_PW.jpg", "6154_PW.jpg",
        "6156_PW.jpg", "6157_PW.jpg", "6158_PW.jpg", "6189_PW.jpg", "6306_PW.jpg",
        "6307_PW.jpg", "6312_PW.jpg", "6314_PW.jpg", "6315_PW.jpg", "6318_pw.jpg",
        "6329_PW.jpg", "6354_PW.jpg", "6355_PW.jpg", "6357_PW.jpg", "6359_PW.jpg",
        "6360_PW.jpg", "6361_PW.jpg", "6362_PW.jpg", "6363_PW.jpg", "6486_PW.jpg",
        "6511_PW.jpg", "6513_PW.jpg", "6518_PW.jpg", "6526_PW.jpg", "6535_PW.jpg",
        "6536_PW.jpg", "6537_PW.jpg", "6538_PW.jpg", "6560_PW.jpg", "6561_PW.jpg",
        "6576_PW.jpg", "6577_PW.jpg", "6580_PW.jpg", "6581_PW.jpg", "6582_PW.jpg",
        "6583_PW.jpg", "6594_PW.jpg", "6595_PW.jpg", "6596_PW.jpg", "6597_PW.jpg",
        "6674_PW.jpg", "6675_PW.jpg", "6676_PW.jpg", "6677_PW.jpg", "6678_PW.jpg",
        "6681_PW.jpg", "6682_PW.jpg", "6683_PW.jpg", "6689_PW.jpg", "6691_PW.jpg",
        "6692_PW.jpg", "6693_PW.jpg", "6694_PW.jpg", "6696_PW.jpg", "6697_PW.jpg",
        "6698_PW.jpg", "6705_PW.jpg", "6708_PW.jpg", "6726_PW.jpg", "6727_PW.jpg",
        "6729_PW.jpg", "6736_PW.jpg", "6747_PW.jpg", "6754_PW.jpg", "6762_PW.jpg",
        "6778_PW.jpg", "6793_PW.jpg", "6794_PW.jpg", "6795_PW.jpg", "6796_PW.jpg",
        "6798_PW.jpg", "6906_PW.jpg", "6909_PW.jpg", "6918_PW.jpg", "6930_PW.jpg",
        "cover.jpg",
    ]},
    {"slug": "cool-colour", "files": [
        "15003_PW.jpg", "15013_PW.jpg", "15014_PW.jpg", "15015_PW.jpg", "15018_PW.jpg",
        "15019_PW.jpg", "15020_PW.jpg", "15022_PW.jpg", "15023_PW.jpg", "15024_PW.jpg",
        "15025_PW.jpg", "15026_PW.jpg", "15027_PW.jpg", "15028_PW.jpg", "15029_PW.jpg",
        "15030_PW.jpg", "15031_PW.jpg", "15032_PW.jpg", "15033_PW.jpg", "15034_PW.jpg",
        "15035_PW.jpg", "15036_PW.jpg", "15052_PW.jpg", "15060_PW.jpg", "15072_PW.jpg",
        "15080_PW.jpg", "15081_PW.jpg", "15082.jpg", "15083_PW.jpg", "15084_PW.jpg",
        "15085_PW.jpg", "15087.jpg", "15088_PW.jpg", "15090_PW.jpg", "15091_PW.jpg",
        "15092_PW.jpg", "15094_PW.jpg", "15119_PW.jpg", "15120_PW.jpg", "15121_PW.jpg",
        "15122_PW.jpg", "15125_PW.jpg", "15126_PW.jpg", "15127_PW.jpg", "15128_PW.jpg",
        "15129_PW.jpg", "15130_PW.jpg", "15131_PW.jpg", "15132_PW.jpg", "15133_PW.jpg",
        "15134_PW.jpg", "15135_PW.jpg", "15136_PW.jpg", "15137_PW.jpg", "15138_PW.jpg",
        "15139_PW.jpg", "15143_PW.jpg", "15144_PW.jpg", "15145_PW.jpg", "15146_PW.jpg",
        "15149_PW.jpg", "cover.jpg",
    ]},
    {"slug": "sshades", "files": [
        "10005.jpg", "10016.jpg", "10018.jpg", "10022.jpg", "10024.jpg", "10025.jpg",
        "10026.jpg", "10027.jpg", "10030.jpg", "10031.jpg", "10032.jpg", "10033.jpg",
        "10034.jpg", "10081.jpg", "10085.jpg", "10088.jpg", "10089.jpg", "10090.jpg",
        "10094.jpg", "10096.jpg", "10141.jpg", "10143.jpg", "10144.jpg", "10145.jpg",
        "10148.jpg", "10149.jpg", "10297.jpg", "10298.jpg", "10299.jpg", "10330.jpg",
        "10344.jpg", "10347.jpg", "10351.jpg", "10375.jpg", "10376.jpg", "10557.jpg",
        "10558.jpg", "10634.jpg", "10635.gif", "10636.jpg", "10637.jpg", "10784.jpg",
        "10792.jpg", "10809.jpg", "10811.jpg", "10813.jpg", "10816.gif", "10822.jpg",
        "10823.jpg", "10824.jpg", "10827.gif", "10832.jpg", "10854.jpg", "10866.jpg",
        "10867.jpg", "10868.jpg", "10869.jpg", "10875.jpg", "10876.jpg", "10878.jpg",
        "10879.jpg", "10882.jpg", "10884.jpg", "10886.jpg", "10889.jpg", "10890.jpg",
        "10891.jpg", "10892.jpg", "10893.jpg", "10896.jpg", "10897.jpg", "10898.jpg",
        "10899.jpg", "6005-5.jpg", "6007-2.jpg", "cover.jpg",
    ]},
    {"slug": "thermo", "files": []},
    {"slug": "thre3", "files": [
        "3003_BS.jpg", "3012_BS.jpg", "3013_BS.jpg", "3014_BS.jpg", "3019_BS.jpg",
        "3020_BS.jpg", "3021_BS.jpg", "3023_BS.jpg", "3030_BS.jpg", "3031_BS.jpg",
        "3032_BS.jpg", "3033_BS.jpg", "3034_BS.jpg", "3035_BS.jpg", "3052_BS.jpg",
        "3056_BS.jpg", "3060_BS.jpg", "3084_BS.jpg", "3085_BS.jpg", "3090_BS.jpg",
        "3091_BS.jpg", "3317_ok_BS.jpg", "3321_ok.jpg", "3333_BS.jpg", "3337_ok_BS.jpg",
        "3339_ok.jpg", "3340_BS.jpg", "3364_ok.jpg", "3365_ok_S.jpg", "3366_BS.jpg",
        "3367_BS.jpg", "3368_BS.jpg", "3369_ok.jpg", "3378_PW.jpg", "3380_PW.jpg",
        "3381_PW.jpg", "3508_ok_BS.jpg", "3509_ok_BS.jpg", "3511_ok_BS.jpg", "3512_ok_BS.jpg",
        "3519_BS.jpg", "3521_ok.jpg", "3527_BS.jpg", "3528_ok.jpg", "3529_ok_P.jpg",
        "3530_BS.jpg", "3531_BS.jpg", "3532_BS.jpg", "3533_BS.jpg", "3534_ok.jpg",
        "3543_BS.jpg", "3544_ok.jpg", "3545_BS.jpg", "3546_ok.jpg", "3547_BS.jpg",
        "3548_ok.jpg", "3549_ok_BS.jpg", "3550_ok_BS.jpg", "3551_ok_BS.jpg", "3552_ok_BS.jpg",
        "3575_ok_BS.jpg", "3579_ok_BS.jpg", "3605_ok.jpg", "3618_BS.jpg", "3619_BS.jpg",
        "3622_BS.jpg", "3623_ok.jpg", "3624_ok.jpg", "3625_BS.jpg", "3626_BS.jpg",
        "3627_BS.jpg", "3628_BS.jpg", "3630_BS.jpg", "3651_ok.jpg", "3653_BS.jpg",
        "3660_ok.jpg", "3661_ok_BS.jpg", "3662_BS.jpg", "3676_ok_BS.jpg", "3678_ok_BS.jpg",
        "3686_PW.jpg", "3716_BS.jpg", "3733_BS.jpg", "3751_BS.jpg", "3752_BS.jpg",
        "3785_ok_BS.jpg", "3786_ok_BS.jpg", "3819_PW.jpg", "3835_ok.jpg", "3846_ok_BS.jpg",
        "3847_ok_BS.jpg", "3849_ok.jpg", "3855_ok_BS.jpg", "3856_ok_BS.jpg", "3857_ok_BS.jpg",
        "3858_BS.jpg", "3859_BS.jpg", "3902_ok_BS.jpg", "3903_ok_BS.jpg", "3907_ok_BS.jpg",
        "3908_BS.jpg", "3911_ok_BS.jpg", "3912_ok.jpg", "3926_PW.jpg", "3942_PW.jpg",
        "cover.jpg",
    ]},
]

_PRODUCT_ID_RE = re.compile(r"^\d+(?:-\d+)?")


def _extract_product_id(filename: str) -> str:
    stem = filename.rsplit(".", 1)[0]
    m = _PRODUCT_ID_RE.match(stem)
    return m.group(0) if m else stem


def seed(apps, schema_editor):
    GalleryCatalogue = apps.get_model("gallery", "GalleryCatalogue")
    GalleryImage = apps.get_model("gallery", "GalleryImage")

    for entry in MANIFEST:
        slug = entry["slug"]
        position = CATALOGUE_ORDER.index(slug) if slug in CATALOGUE_ORDER else len(CATALOGUE_ORDER)
        catalogue, created = GalleryCatalogue.objects.get_or_create(
            slug=slug,
            defaults={"label": CATALOGUE_LABELS.get(slug, slug.title()), "position": position},
        )
        if not created:
            continue  # already has data — don't touch it again on a re-run

        img_position = 0
        for filename in entry["files"]:
            path = f"/assets/img/gallery/{slug}/{filename}"
            if filename.lower().startswith("cover."):
                catalogue.cover_image = path
                catalogue.save(update_fields=["cover_image"])
                continue
            GalleryImage.objects.create(
                catalogue=catalogue,
                image=path,
                product_id=_extract_product_id(filename),
                position=img_position,
            )
            img_position += 1


def unseed(apps, schema_editor):
    GalleryCatalogue = apps.get_model("gallery", "GalleryCatalogue")
    GalleryCatalogue.objects.filter(
        slug__in=[e["slug"] for e in MANIFEST]
    ).delete()  # cascades to images


class Migration(migrations.Migration):

    dependencies = [
        ("gallery", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
