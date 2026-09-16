from rest_framework.throttling import AnonRateThrottle


class InquiryThrottle(AnonRateThrottle):
    rate  = "10/minute"
    scope = "inquiry"


class FormSubmitThrottle(AnonRateThrottle):
    rate  = "10/minute"
    scope = "form_submit"
