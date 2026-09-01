from rest_framework.throttling import AnonRateThrottle


class InquiryThrottle(AnonRateThrottle):
    rate  = "10/minute"
    scope = "inquiry"
