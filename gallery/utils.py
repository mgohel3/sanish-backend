"""Helpers for the Applications photo tagging (spaces) + bulk CSV import."""
import csv
import io
import re

# ── normalisation ────────────────────────────────────────────────────────────

def stem_key(name: str) -> str:
    """Matching key for a photo filename — case-, extension- and separator-insensitive.

    ``Thre3_3003_01.JPG``, ``thre3-3003-01.webp`` and ``/assets/img/x/thre3_3003_01.jpg``
    all give ``thre3300301``. (Photos are converted to WebP on upload, so the extension can
    never be part of the key.)
    """
    base = (name or "").replace("\\", "/").split("/")[-1]
    stem = base.rsplit(".", 1)[0] if "." in base else base
    return re.sub(r"[^a-z0-9]", "", stem.lower())


def tag_key(label: str) -> str:
    """Matching key for a space/tag or catalogue name: ``Bathroom & Vanity`` == ``bathroom and vanity``;
    a trailing plural ``s`` is ignored (``Wardrobe`` == ``Wardrobes``, ``Close-up`` == ``Close-ups``)."""
    s = (label or "").lower().replace("&", " and ")
    s = re.sub(r"[^a-z0-9]", "", s)
    return s[:-1] if len(s) > 3 and s.endswith("s") else s


# ── CSV parsing ──────────────────────────────────────────────────────────────

HEADER_ALIASES = {
    "filename": {"imagefilename", "filename", "image", "file", "imagename", "photo", "photofilename"},
    "sku": {"sku", "productcode", "code", "productid"},
    "catalogue": {"catalogue", "catalog", "collection"},
    "tags": {"tags", "tag", "spaces", "space"},
}


def _hkey(h):
    return re.sub(r"[^a-z0-9]", "", (h or "").lower())


def decode_upload(raw: bytes) -> str:
    for enc in ("utf-8-sig", "cp1252"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def parse_tag_csv(text: str):
    """Returns (rows, error). Each row: dict(line, filename, sku, catalogue, tags[list])."""
    text = text.strip("﻿\r\n ")
    if not text:
        return [], "The file is empty."
    try:
        dialect = csv.Sniffer().sniff(text[:4096], delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel
    reader = csv.reader(io.StringIO(text), dialect)
    try:
        header = next(reader)
    except StopIteration:
        return [], "The file is empty."
    cols = {}
    for i, h in enumerate(header):
        k = _hkey(h)
        for field, aliases in HEADER_ALIASES.items():
            if k in aliases and field not in cols:
                cols[field] = i
    if "filename" not in cols:
        return [], ("Couldn't find the image filename column. Expected columns: "
                    "image filename, SKU, catalogue, tags.")
    rows = []
    for n, rec in enumerate(reader, start=2):
        if not any((c or "").strip() for c in rec):
            continue
        def cell(field):
            i = cols.get(field)
            return (rec[i].strip() if i is not None and i < len(rec) else "")
        tags = [t.strip() for t in re.split(r"[|]", cell("tags")) if t.strip()]
        rows.append({
            "line": n, "filename": cell("filename"), "sku": cell("sku"),
            "catalogue": cell("catalogue"), "tags": tags,
        })
    return rows, None


# ── matching / preview ───────────────────────────────────────────────────────

def build_preview(rows):
    """Resolve CSV rows against the CMS. Pure read — nothing is written here."""
    from .models import GalleryCatalogue, GalleryImage, GallerySpace

    spaces = {tag_key(s.label): s for s in GallerySpace.objects.filter(enabled=True)}
    for s in GallerySpace.objects.filter(enabled=True):
        spaces.setdefault(tag_key(s.slug), s)
    catalogues = {}
    for c in GalleryCatalogue.objects.all():
        catalogues[tag_key(c.label)] = c
        catalogues.setdefault(tag_key(c.slug), c)

    by_key = {}
    for img in GalleryImage.objects.select_related("catalogue"):
        by_key.setdefault(stem_key(img.filename or img.image), []).append(img)

    seen = {}
    results = []
    for r in rows:
        res = {**r, "status": "ok", "notes": [], "image_id": None, "image_src": "",
               "current_catalogue": "", "unknown_tags": [], "space_ids": [], "space_labels": [],
               "set_tags": bool(r["tags"])}
        if not r["filename"]:
            res["status"] = "error"
            res["notes"].append("No filename on this row.")
            results.append(res)
            continue

        key = stem_key(r["filename"])
        cands = by_key.get(key, [])

        cat = None
        if r["catalogue"]:
            cat = catalogues.get(tag_key(r["catalogue"]))
            if not cat:
                res["notes"].append(f"Unknown catalogue “{r['catalogue']}” — ignored.")
            elif len(cands) > 1:
                narrowed = [c for c in cands if c.catalogue_id == cat.pk]
                if narrowed:
                    cands = narrowed

        if not cands:
            res["status"] = "not_found"
            res["notes"].append("No photo with this filename in the CMS — upload it first (Applications → catalogue → Upload Photos).")
            results.append(res)
            continue
        if len(cands) > 1:
            res["status"] = "ambiguous"
            res["notes"].append("More than one photo has this filename — add the catalogue column to pick one.")
            results.append(res)
            continue

        img = cands[0]
        res["image_id"] = img.pk
        res["image_src"] = img.image
        res["current_catalogue"] = img.catalogue.label
        if cat and cat.pk != img.catalogue_id:
            res["notes"].append(f"CSV says {cat.label}, but this photo is in {img.catalogue.label} — left where it is.")

        ids, labels, unknown = [], [], []
        for t in r["tags"]:
            sp = spaces.get(tag_key(t))
            if sp:
                if sp.pk not in ids:
                    ids.append(sp.pk)
                    labels.append(sp.label)
            else:
                unknown.append(t)
        res["space_ids"], res["space_labels"], res["unknown_tags"] = ids, labels, unknown
        # Only touch a photo's tags when the row names at least one VALID tag — a row whose tags are
        # all unknown must never wipe the tags the photo already has.
        res["set_tags"] = bool(ids)
        if unknown:
            res["notes"].append("Tag not found: " + ", ".join(unknown) + " — skipped (not created).")
        if not r["tags"]:
            res["notes"].append("No tags in this row — existing tags left unchanged.")

        if key in seen:
            results[seen[key]]["status"] = "duplicate"
            results[seen[key]]["notes"].append("Same filename appears again later in the CSV — the later row wins.")
        seen[key] = len(results)
        results.append(res)

    unknown_tags = {}
    for r in results:
        for t in r["unknown_tags"]:
            unknown_tags[t] = unknown_tags.get(t, 0) + 1
    ok_rows = [r for r in results if r["status"] in ("ok", "duplicate") and r["image_id"] and r["status"] != "duplicate"]
    summary = {
        "total": len(results),
        "matched": len(ok_rows),
        "not_found": [r["filename"] for r in results if r["status"] == "not_found"],
        "ambiguous": [r["filename"] for r in results if r["status"] == "ambiguous"],
        "errors": [r for r in results if r["status"] == "error"],
        "unknown_tags": sorted(unknown_tags.items(), key=lambda kv: (-kv[1], kv[0])),
        "duplicates": sum(1 for r in results if r["status"] == "duplicate"),
    }
    return results, summary


def commit_rows(results):
    """Apply resolved rows. Filename is the key — only existing photos are updated, never created."""
    from django.db import transaction
    from .models import GalleryImage, GallerySpace

    updated = 0
    with transaction.atomic():
        for r in results:
            if r["status"] != "ok" or not r["image_id"]:
                continue
            img = GalleryImage.objects.filter(pk=r["image_id"]).first()
            if not img:
                continue
            if r["sku"]:
                img.sku = r["sku"][:60]
                img.save(update_fields=["sku"])
            if r["set_tags"]:
                img.spaces.set(GallerySpace.objects.filter(pk__in=r["space_ids"]))
            updated += 1
    return updated
