import json

from django import template

register = template.Library()


@register.filter
def dictkey(mapping, key):
    """Look up ``mapping[key]`` with a variable key (unsupported in the DTL)."""
    try:
        return mapping.get(key, "")
    except AttributeError:
        return ""


@register.filter
def jsonify(value):
    """Compact JSON for embedding in an attribute (used to seed Alpine repeaters)."""
    return json.dumps(value if value is not None else [])


@register.filter
def jsonify_blank(subfields):
    """A blank row object for a repeater, given its list of sub-field specs."""
    blank = {}
    for sf in subfields or []:
        blank[sf["name"]] = False if sf.get("type") == "bool" else ""
    return json.dumps(blank)
