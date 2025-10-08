"""Simple static file web server.

This module provides a small HTTP server that serves files from the current
working directory. It performs basic error handling to ensure that only files
within the directory are served and that helpful responses are returned when
requests cannot be fulfilled.
"""
from __future__ import annotations

import argparse
import http.server
import logging
import mimetypes
import os
import posixpath
from pathlib import Path
from typing import Tuple

LOGGER = logging.getLogger(__name__)


def _safe_path(root: Path, request_path: str) -> Path | None:
    """Return the resolved filesystem path for *request_path* if it is safe.

    Args:
        root: The directory that is considered the root of served files.
        request_path: The URL path from the incoming request.

    Returns:
        A :class:`pathlib.Path` to the requested file if it resides inside the
        root directory, or ``None`` if the request attempts to traverse outside
        the root.
    """
    # Remove query parameters and fragments.
    request_path = request_path.split("?")[0].split("#")[0]
    # Normalize path to remove .. and . segments.
    normalized = posixpath.normpath(request_path)
    # Remove the leading slash to work with relative paths.
    relative = normalized.lstrip("/")
    candidate = (root / relative).resolve()

    try:
        candidate.relative_to(root)
    except ValueError:
        return None

    return candidate


class StaticFileHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler that serves files from a fixed directory."""

    server_version = "SimpleStaticHTTP/1.0"

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        self._handle_request(send_body=True)

    def do_HEAD(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        self._handle_request(send_body=False)

    def _handle_request(self, *, send_body: bool) -> None:
        root = Path(self.server.root_directory)
        path = _safe_path(root, self.path)
        if path is None:
            self._send_error(403, "Forbidden", "Access outside the root directory is not allowed.")
            return

        if path.is_dir():
            index_file = path / "index.html"
            if index_file.exists():
                path = index_file
            else:
                self._send_error(403, "Forbidden", "Directory listing is not permitted.")
                return

        if not path.exists():
            self._send_error(404, "Not Found", "The requested resource could not be found.")
            return

        if not os.access(path, os.R_OK):
            self._send_error(403, "Forbidden", "The requested resource is not readable.")
            return

        ctype = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        try:
            with path.open("rb") as file_obj:
                content = file_obj.read() if send_body else b""
        except OSError as error:
            LOGGER.exception("Failed to read %s", path)
            self._send_error(500, "Internal Server Error", str(error))
            return

        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(path.stat().st_size))
        self.end_headers()
        if send_body:
            self.wfile.write(content)

    def log_message(self, format: str, *args) -> None:  # noqa: A003 - match BaseHTTPRequestHandler
        LOGGER.info("%s - - %s", self.client_address[0], format % args)

    def _send_error(self, code: int, message: str, explanation: str) -> None:
        self.send_error(code, message, explanation=explanation)


class StaticFileServer(http.server.ThreadingHTTPServer):
    """HTTP server that exposes files from a specific directory."""

    def __init__(self, server_address: Tuple[str, int], directory: Path):
        self.root_directory = directory.resolve()
        super().__init__(server_address, StaticFileHandler)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Serve files from the current directory.")
    parser.add_argument("--host", default="0.0.0.0", help="Host interface to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    parser.add_argument(
        "--directory",
        default=Path.cwd(),
        type=Path,
        help="Directory to serve (default: current working directory)",
    )
    return parser.parse_args()


def main() -> None:
    """Start the static file server."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = parse_args()
    directory = args.directory.resolve()

    if not directory.exists() or not directory.is_dir():
        raise SystemExit(f"The directory {directory} does not exist or is not a directory.")

    server_address = (args.host, args.port)
    httpd = StaticFileServer(server_address, directory)
    LOGGER.info("Serving %s on http://%s:%s", directory, args.host, args.port)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        LOGGER.info("Shutting down server after keyboard interrupt.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
