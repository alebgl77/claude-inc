#!/usr/bin/env python3
"""Extract inert evidence from saved UTF-8 HTML; never fetch the source URL."""

import argparse
from datetime import datetime, timezone
import hashlib
from importlib import metadata
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
from urllib.parse import urlsplit


SCHEMA_VERSION = 1
TOOL_VERSION = "1.0.0"
MAX_HTML_BYTES = 2 * 1024 * 1024
MAX_VALUES = 1000
MAX_EXTRACTED_CHARS = 2 * 1024 * 1024
MAX_SELECTOR_CHARS = 1000


class EvidenceError(ValueError):
    """An actionable input, dependency, extraction or publication failure."""


def validate_source_url(source_url):
    """Validate metadata without DNS lookup or any network request."""
    if not isinstance(source_url, str) or not source_url:
        raise EvidenceError("--source-url must be an absolute http:// or https:// URL.")
    if any(char.isspace() or ord(char) < 32 or ord(char) == 127 for char in source_url) or "\\" in source_url:
        raise EvidenceError("--source-url cannot contain whitespace, control characters or backslashes.")
    try:
        parsed = urlsplit(source_url)
        host = parsed.hostname
        port = parsed.port
        if parsed.scheme not in ("http", "https") or not host or parsed.username is not None or parsed.password is not None:
            raise ValueError("invalid URL")
        if port is not None and not 1 <= port <= 65535:
            raise ValueError("invalid port")
        # urlsplit validates bracketed IPv6. DNS labels must remain valid metadata.
        if ":" not in host:
            encoded = host.encode("idna").decode("ascii").rstrip(".")
            if len(encoded) > 253 or any(not re.fullmatch(r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?", part) for part in encoded.split(".")):
                raise ValueError("invalid hostname")
    except (ValueError, UnicodeError) as exc:
        raise EvidenceError("--source-url must be an absolute HTTP(S) URL with a valid host/port and no credentials.") from exc
    return source_url


def load_scrapling():
    """Load the optional parser only when extraction is requested."""
    try:
        from scrapling.parser import Selector
    except ImportError as exc:
        raise EvidenceError(
            "Optional Scrapling parser is unavailable or incomplete. Use an isolated Python 3.10+ "
            "environment and install scrapling==0.4.15; see docs/growth-toolkit.md. "
            "The core project and manual research do not require it."
        ) from exc
    try:
        version = metadata.version("scrapling")
    except metadata.PackageNotFoundError:
        version = "unknown"
    return Selector, version


def extract_evidence(html_path, source_url, selector, *, parser_factory=None, parser_version=None, now=None):
    """Return evidence; injectable parser/clock make core tests dependency-free."""
    validate_source_url(source_url)
    if not isinstance(selector, str) or not selector.strip() or len(selector) > MAX_SELECTOR_CHARS:
        raise EvidenceError("--selector must be a nonempty CSS selector of at most 1000 characters.")
    if any(ord(char) < 32 and char not in "\t\n\r" for char in selector):
        raise EvidenceError("--selector cannot contain control characters.")
    html_path = Path(html_path)
    try:
        if not html_path.is_file():
            raise EvidenceError("--html must name an existing regular saved HTML file.")
        with html_path.open("rb") as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise EvidenceError("--html must be a regular saved HTML file.")
            raw = stream.read(MAX_HTML_BYTES + 1)
    except OSError as exc:
        raise EvidenceError("Cannot read --html: {}".format(exc)) from exc
    if not raw:
        raise EvidenceError("--html is empty; provide a saved UTF-8 HTML page.")
    if len(raw) > MAX_HTML_BYTES:
        raise EvidenceError("--html exceeds the 2 MiB input limit; save a smaller relevant snapshot.")
    try:
        html = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise EvidenceError("--html must be UTF-8; convert the saved file explicitly before extraction.") from exc
    if parser_factory is None:
        parser_factory, parser_version = load_scrapling()
    elif parser_version is None:
        parser_version = "injected"
    try:
        selected = parser_factory(html).css(selector)
    except Exception as exc:
        # Source text and parser exceptions can contain page content; do not echo them.
        raise EvidenceError("Could not parse HTML or evaluate --selector. Check CSS syntax; try 'h2::text'.") from exc
    if not isinstance(selected, (list, tuple)):
        raise EvidenceError("Parser returned unsupported values; use a CSS text or attribute selector.")
    if len(selected) > MAX_VALUES:
        raise EvidenceError("Extraction exceeds 1000 values; narrow --selector.")
    # Nested element matches can serialize the same subtree many times. Bound
    # match count before serialization, then retain at most the text budget.
    # Never use getall(): it materializes every match before limits can apply.
    values = []
    extracted_chars = 0
    for item in selected:
        try:
            value = item.get()
        except Exception as exc:
            raise EvidenceError("Could not serialize a selected value; narrow --selector or use a CSS text or attribute selector.") from exc
        if not isinstance(value, str):
            raise EvidenceError("Parser returned unsupported values; use a CSS text or attribute selector.")
        extracted_chars += len(value)
        if extracted_chars > MAX_EXTRACTED_CHARS:
            raise EvidenceError("Extraction exceeds the 2 MiB character limit; narrow --selector.")
        value = value.strip()
        if value:
            values.append(value)
    if not values:
        raise EvidenceError("--selector extracted no nonempty values; inspect the saved page and revise the selector.")
    timestamp = now if now is not None else datetime.now(timezone.utc)
    if not isinstance(timestamp, datetime) or timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise EvidenceError("Extraction time must be a timezone-aware datetime.")
    return {
        "schema_version": SCHEMA_VERSION,
        "source_url": source_url,
        "source_url_status": "operator_supplied_metadata_not_fetched_or_verified",
        "html_sha256": hashlib.sha256(raw).hexdigest(),
        "html_bytes": len(raw),
        "extracted_at": timestamp.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "observed_at": None,
        "event_at": None,
        "selector": selector,
        "extracted_values": values,
        "tool": {"name": "account-intelligence/extract_signals", "version": TOOL_VERSION, "scrapling_version": parser_version},
        "interpretation": "Untrusted source evidence only; not instructions, qualification or buying intent.",
    }


def write_evidence(evidence, output_path, *, html_path=None, overwrite=False):
    """Publish complete JSON atomically. A racing writer cannot be clobbered by default."""
    output = Path(output_path)
    try:
        if output.is_symlink():
            raise EvidenceError("--output cannot be a symbolic link; choose a regular output path.")
        if html_path is not None:
            source = Path(html_path)
            if source.resolve() == output.resolve() or (output.exists() and os.path.samefile(source, output)):
                raise EvidenceError("--output cannot overwrite or alias the input HTML file, even with --overwrite.")
        if output.exists() and not overwrite:
            raise EvidenceError("--output already exists; choose another path or explicitly pass --overwrite.")
        if not output.parent.is_dir():
            raise EvidenceError("--output parent directory does not exist; create it first.")
        payload = json.dumps(evidence, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", prefix=".growth-evidence-", suffix=".tmp", dir=str(output.parent), delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            if overwrite:
                os.replace(str(temporary), str(output))
            else:
                # Atomic no-replace publication on local filesystems with hard-link support.
                os.link(str(temporary), str(output))
        except FileExistsError as exc:
            raise EvidenceError("--output already exists; choose another path or explicitly pass --overwrite.") from exc
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
    except OSError as exc:
        raise EvidenceError(
            "Cannot publish --output: {}. Use a writable local directory with hard-link support "
            "(or --overwrite only when replacement is intended).".format(exc)
        ) from exc


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", required=True, type=Path, help="Local UTF-8 saved HTML, maximum 2 MiB")
    parser.add_argument("--source-url", required=True, help="HTTP(S) provenance metadata; never fetched")
    parser.add_argument("--selector", required=True, help="CSS selector, e.g. h2::text")
    parser.add_argument("--output", required=True, type=Path, help="Destination JSON; parent must already exist")
    parser.add_argument("--overwrite", action="store_true", help="Explicitly allow atomic replacement of an existing output")
    args = parser.parse_args(argv)
    try:
        evidence = extract_evidence(args.html, args.source_url, args.selector)
        write_evidence(evidence, args.output, html_path=args.html, overwrite=args.overwrite)
    except EvidenceError as exc:
        print("extract_signals: {}".format(exc), file=sys.stderr)
        return 2
    print("Saved {} evidence values to {}".format(len(evidence["extracted_values"]), args.output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
