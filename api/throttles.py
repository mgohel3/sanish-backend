from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

SAFE_METHODS = ("GET", "HEAD", "OPTIONS")


class ReadExemptAnonThrottle(AnonRateThrottle):
    """The global 'anon' limit, applied to WRITES only (POST/PUT/PATCH/DELETE).

    The storefront renders pages on the server, and every one of those calls to the
    public read-only API reaches Django from the same address (the website
    container, via nginx). Counting them against one shared 60/min bucket made the
    API answer 429 under even light load, the storefront then fell back to its
    built-in data and cached a 404 page. Reads are cheap and public, so they are not
    limited here; login and the form/inquiry endpoints keep their own limits.
    """

    def allow_request(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return super().allow_request(request, view)


class ReadExemptUserThrottle(UserRateThrottle):
    """The global 'user' limit, writes only (see ReadExemptAnonThrottle)."""

    def allow_request(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return super().allow_request(request, view)


class InquiryThrottle(AnonRateThrottle):
    rate  = "10/minute"
    scope = "inquiry"


class FormSubmitThrottle(AnonRateThrottle):
    rate  = "10/minute"
    scope = "form_submit"
