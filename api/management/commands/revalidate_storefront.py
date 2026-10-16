from django.core.management.base import BaseCommand

from api.revalidate import fire_now


class Command(BaseCommand):
    help = "Drop the storefront's cached pages/data now (run after imports or scripts that change CMS data outside the CMS)."

    def handle(self, *args, **options):
        fire_now()
        self.stdout.write("storefront revalidation requested")
