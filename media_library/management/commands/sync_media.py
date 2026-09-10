"""
Register on-disk media files and (optionally) import images used by the
website frontend into the Media Library.

    python manage.py sync_media                 # scan MEDIA_ROOT only
    python manage.py sync_media --import-frontend
    python manage.py sync_media --import-dir "C:/path/to/images" --folder "Legacy"

Never deletes or overwrites existing MediaAsset rows.
"""
from django.core.management.base import BaseCommand

from media_library.utils import scan_media_root, import_external_dir, get_import_dirs


class Command(BaseCommand):
    help = "Sync the Media Library with files on disk / the frontend."

    def add_arguments(self, parser):
        parser.add_argument("--import-frontend", action="store_true",
                            help="Also import images from the configured frontend public folders.")
        parser.add_argument("--import-dir", default=None,
                            help="Import supported media from this directory (recursive).")
        parser.add_argument("--folder", default=None,
                            help="Folder name to place imported assets in.")
        parser.add_argument("--no-scan", action="store_true",
                            help="Skip the MEDIA_ROOT disk scan.")

    def handle(self, *args, **opts):
        if not opts["no_scan"]:
            added, skipped = scan_media_root()
            self.stdout.write(self.style.SUCCESS(
                f"Disk scan: {added} registered, {skipped} already known."
            ))

        if opts["import_dir"]:
            a, s = import_external_dir(opts["import_dir"], folder_name=opts["folder"])
            self.stdout.write(self.style.SUCCESS(
                f"Imported {a}, skipped {s} from {opts['import_dir']}"
            ))

        if opts["import_frontend"]:
            for d in get_import_dirs():
                if d.is_dir():
                    a, s = import_external_dir(str(d), folder_name=opts["folder"] or "Frontend")
                    self.stdout.write(self.style.SUCCESS(
                        f"Imported {a}, skipped {s} from {d}"
                    ))
                else:
                    self.stdout.write(self.style.WARNING(f"Not found: {d}"))
