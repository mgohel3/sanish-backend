"""Finish code -> texture group, from the client's filter workbooks (Sanish_Filters_final.xlsx for laminates,
Sanish_Thermo_Filters.xlsx for Thermo). A product's finish CODE (UG, SF, GS ...) always implies its texture, so the CMS
fills the Texture dropdown from the code when it is left blank. Codes the client left out of the filter (NK, PR) stay blank."""
import re

LAMINATE_CODE_TEXTURE = {
 "AB": "Abstract",
 "AC": "Abstract",
 "AG": "Stone",
 "AK": "Stone",
 "AL": "Abstract",
 "AM": "Matte",
 "AP": "Wooden",
 "AX": "Abstract",
 "AZ": "Sparkle",
 "BM": "Wooden",
 "BN": "Abstract",
 "BR": "Stone",
 "CD": "Abstract",
 "CE": "Abstract",
 "CR": "Stone",
 "CS": "Wooden",
 "CT": "Stone",
 "CV": "Abstract",
 "DB": "Abstract",
 "DD": "Abstract",
 "DF": "Flute",
 "DL": "Sparkle",
 "DN": "Abstract",
 "DR": "Wooden",
 "EN": "Abstract",
 "FG": "Flute",
 "FH": "Abstract",
 "FK": "Flute",
 "FS": "Flute",
 "FT": "Flute",
 "FW": "Flute",
 "GR": "Stone",
 "HB": "Abstract",
 "HT": "Wooden",
 "HZ": "Wooden",
 "JF": "Wooden",
 "LG": "Wooden",
 "LK": "Abstract",
 "LR": "Leather",
 "LX": "Wooden",
 "MC": "Gloss",
 "MF": "Flute",
 "MG": "Wooden",
 "ML": "Wooden",
 "MM": "Wooden",
 "MN": "Abstract",
 "MR": "Sparkle",
 "MW": "Wooden",
 "ND": "Stone",
 "NL": "Stone",
 "OG": "Wooden",
 "OX": "Abstract",
 "OZ": "Wooden",
 "PL": "Leather",
 "PS": "Sparkle",
 "PW": "Wooden",
 "RL": "Wooden",
 "RM": "Wooden",
 "RP": "Wooden",
 "SC": "Wooden",
 "SE": "Stone",
 "SF": "Suede",
 "SG": "Wooden",
 "SH": "Wooden",
 "SL": "Abstract",
 "SM": "Matte",
 "SN": "Matte",
 "SP": "Wooden",
 "SS": "Wooden",
 "SSN": "Wooden",
 "UG": "Gloss",
 "VF": "Flute",
 "VR": "Wooden",
 "VS": "Stone",
 "VZ": "Wooden",
 "ZK": "Abstract"
}

THERMO_CODE_TEXTURE = {"GS": "Gloss", "SN": "Matte", "MT": "Sparkle", "MS": "Sparkle"}
# Thermo textured designs carry no finish code, only a name in the SKU ("9100 STONE").
THERMO_NAME_TEXTURE = {"STONE": "Stone", "MICRO LINE": "Micro Line", "CRISS CROSS": "Abstract", "CANVAS": "Abstract",
                       "BUBBLE": "Abstract", "WEAVE": "Leather", "METALLIC WEAVE": "Leather"}


def derive_texture(finish, sku="", thermo=False):
    """Texture group implied by a finish code (or, for Thermo, by the SKU's code/name); '' when unknown."""
    code = (finish or "").strip().upper()
    if thermo:
        if code in THERMO_CODE_TEXTURE:
            return THERMO_CODE_TEXTURE[code]
        text = re.sub(r"[0-9()]+", " ", (sku or "").upper())
        text = " ".join(text.split())
        for tok in text.split():
            if tok in THERMO_CODE_TEXTURE:
                return THERMO_CODE_TEXTURE[tok]
        for name, tex in THERMO_NAME_TEXTURE.items():
            if name in text:
                return tex
        return ""
    return LAMINATE_CODE_TEXTURE.get(code, "")
