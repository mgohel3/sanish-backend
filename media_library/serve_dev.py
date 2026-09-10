"""
Dev-only media serving WITH HTTP Range support.

``django.views.static.serve`` (used by the ``DEBUG``-time ``static()`` helper in
config/urls.py) streams the whole file with a ``200`` and no ``Accept-Ranges``
header. Chrome and Safari ``<video>`` elements need ``206 Partial Content``
responses to begin playback and to seek, so CMS-hosted ``.mp4`` files look
"broken" when served by ``runserver`` in development.

This view adds minimal RFC 7233 single-range handling. Staging serves media
through nginx and production through S3/R2 — both already support ranges — so
this module is only ever wired up when ``settings.DEBUG`` is true.
"""
import mimetypes
import os
import re

from django.http import FileResponse, Http404, HttpResponse, StreamingHttpResponse
from django.utils._os import safe_join
from django.utils.http import http_date

_RANGE_RE = re.compile(r"bytes=(\d+)-(\d*)", re.IGNORECASE)
_CHUNK = 64 * 1024


def _stream(fh, remaining):
    try:
        while remaining > 0:
            data = fh.read(min(_CHUNK, remaining))
            if not data:
                break
            remaining -= len(data)
            yield data
    finally:
        fh.close()


def serve_media(request, path, document_root=None):
    full_path = safe_join(document_root, path)
    if not os.path.isfile(full_path):
        raise Http404(path)

    size = os.path.getsize(full_path)
    content_type = mimetypes.guess_type(full_path)[0] or "application/octet-stream"
    range_match = _RANGE_RE.match(request.META.get("HTTP_RANGE", "") or "")

    if range_match:
        start = int(range_match.group(1))
        end = int(range_match.group(2) or size - 1)
        end = min(end, size - 1)
        if start >= size or start > end:
            resp = HttpResponse(status=416)
            resp["Content-Range"] = f"bytes */{size}"
            resp["Accept-Ranges"] = "bytes"
            return resp
        fh = open(full_path, "rb")
        fh.seek(start)
        resp = StreamingHttpResponse(
            _stream(fh, end - start + 1),
            status=206,
            content_type=content_type,
        )
        resp["Content-Length"] = str(end - start + 1)
        resp["Content-Range"] = f"bytes {start}-{end}/{size}"
    else:
        resp = FileResponse(open(full_path, "rb"), content_type=content_type)
        resp["Content-Length"] = str(size)

    resp["Accept-Ranges"] = "bytes"
    resp["Last-Modified"] = http_date(os.path.getmtime(full_path))
    return resp
