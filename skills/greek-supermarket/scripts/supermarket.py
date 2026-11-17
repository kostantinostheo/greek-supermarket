#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "cryptography>=46.0",
#     "httpx>=0.28",
# ]
# ///
"""Query Greek supermarket prices.

Fetches the public price feed, normalizes it, caches it on disk for 60 minutes
and prints compact results meant to be read by an AI assistant.

Usage:
    uv run supermarket.py categories
    uv run supermarket.py merchants
    uv run supermarket.py count
    uv run supermarket.py search "γαλα δελτα" [--category C] [--merchant M]
    uv run supermarket.py category "<exact category>" [--grep TEXT]
    uv run supermarket.py merchant "<exact merchant>" [--grep TEXT]
"""
import argparse
import base64
import difflib
import hashlib
import json
import os
import re
import sys
import tempfile
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import httpx
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from category_mappings import normalize_category

URL = 'U2FsdGVkX1/YBn4z5uesn0+15ThnAT0eD+zTr6Vbvk4AMEqF/wx6sYe76qV/xP6Q3d7Vvz063fs3Ytf7K2KtjIzaPPf58FDDcMGnplJXf2vPl9sjN6j1ng8jS+Q4kulVQvFa+sZcgpDI/2vXm4iqpaO7Whh6dS0Sqe18jx003yI='
CACHE_TTL_SECONDS = 60 * 60  # refresh the data only if older than 60 minutes


# --------------------------------------------------------------------------- #
# Fetching
# --------------------------------------------------------------------------- #

def _evp_bytes_to_key(passphrase: bytes, salt: bytes, key_len: int = 32, iv_len: int = 16):
    # OpenSSL's EVP_BytesToKey (MD5, 1 iteration) - the key derivation CryptoJS uses
    derived = b""
    block = b""
    while len(derived) < key_len + iv_len:
        block = hashlib.md5(block + passphrase + salt).digest()
        derived += block
    return derived[:key_len], derived[key_len:key_len + iv_len]


def decrypt(encrypted):
    raw = base64.b64decode(encrypted)
    salt = raw[8:16]  # layout: "Salted__" + 8 byte salt + ciphertext
    key, iv = _evp_bytes_to_key("=l!RoGMxgMko=88Z4#5*?Vl.@".encode("utf-8"), salt)
    decryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
    padded = decryptor.update(raw[16:]) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    return (unpadder.update(padded) + unpadder.finalize()).decode("utf-8")


def fetch_data():
    cid = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    response = httpx.get(f"{decrypt(URL)}{cid}", follow_redirects=True, timeout=60)
    response.raise_for_status()
    data = response.json()
    return ((data.get("context") or {}).get("MAPP_PRODUCTS") or {}).get("result") or {}


# --------------------------------------------------------------------------- #
# Transforming
# --------------------------------------------------------------------------- #

def flatten_categories(cats, mapping=None):
    """Recursively extracts all category UUIDs into a flat map."""
    if mapping is None:
        mapping = {}
    for cat in cats or []:
        if cat.get("uuid") and cat.get("name"):
            mapping[cat["uuid"]] = cat["name"].lower()
        flatten_categories(cat.get("sub_categories"), mapping)
        flatten_categories(cat.get("sub_sub_categories"), mapping)
    return mapping


def transform_data(result, category_map):
    merchant_map = {m.get("merchant_uuid"): m.get("name") or "" for m in (result.get("merchants") or [])}
    products = []
    for product in result.get("products") or []:
        categories = product.get("category")
        first = categories[0] if categories else None
        products.append({
            "name": (product.get("name") or "").lower(),
            "barcode": product.get("barcode"),
            "category": normalize_category(category_map.get(first) or str(first or "")) or "Λοιπά",
            "retailer_prices": [
                {
                    "merchant_name": merchant_map.get(p.get("merchant_uuid")) or f"Merchant {p.get('merchant_uuid')}",
                    "price": p.get("price"),
                    "price_normalized": p.get("price_normalized"),
                }
                for p in product.get("prices") or []
            ],
        })
    return products


# --------------------------------------------------------------------------- #
# Cache (every invocation is a new process, so the cache lives on disk)
# --------------------------------------------------------------------------- #

def _cache_file() -> Path:
    base = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")
    path = base / "greek-supermarket" / "data.json"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        path = Path(tempfile.gettempdir()) / "greek-supermarket-data.json"
    return path


def load_data(refresh=False):
    cache = _cache_file()
    if not refresh and cache.exists() and time.time() - cache.stat().st_mtime < CACHE_TTL_SECONDS:
        try:
            return json.loads(cache.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            pass  # corrupt cache: fall through and refetch

    raw = fetch_data()
    data = {
        "merchants": sorted(m["name"] for m in raw.get("merchants") or [] if m.get("name")),
        "products": transform_data(raw, flatten_categories(raw.get("categories"))),
    }
    try:
        tmp = cache.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        tmp.replace(cache)
    except OSError:
        pass  # a read-only cache location only costs speed
    return data


# --------------------------------------------------------------------------- #
# Querying
# --------------------------------------------------------------------------- #

def normalize_text(text=""):
    """Lowercase and strip accents so 'Γάλα' matches 'γαλα'."""
    return re.sub(r"[̀-ͯ]", "", unicodedata.normalize("NFD", (text or "").lower()))


def matches_all_words(name, query):
    haystack = normalize_text(name)
    return all(word in haystack for word in normalize_text(query).split())


def resolve(value, options, kind, command):
    """Match a category/merchant name ignoring case and accents, or exit with suggestions."""
    wanted = normalize_text(value)
    for option in options:
        if normalize_text(option) == wanted:
            return option
    close = difflib.get_close_matches(value, options, n=5, cutoff=0.4)
    hint = f" Did you mean: {', '.join(close)}?" if close else ""
    sys.exit(f"Unknown {kind}: {value!r}.{hint} Run the '{command}' command for the exact names.")


def price_label(rp):
    unit = rp.get("price_normalized")
    return f"{rp['merchant_name']} €{rp['price']:.2f}" + (f" (€{unit:.2f}/unit)" if unit is not None else "")


def cheapest(product):
    prices = [rp["price"] for rp in product["retailer_prices"] if rp.get("price") is not None]
    return min(prices) if prices else float("inf")


def print_products(products, args, merchant=None):
    """Print one compact line per product, with the cheapest merchant first."""
    if merchant:
        for p in products:  # keep only the chosen merchant's own price
            p["retailer_prices"] = [rp for rp in p["retailer_prices"] if rp["merchant_name"] == merchant]
    products.sort(key=(lambda p: p["name"]) if args.sort == "name" else cheapest)
    total = len(products)
    shown = products[: args.limit]

    if args.json:
        print(json.dumps({"total": total, "shown": len(shown), "results": shown}, ensure_ascii=False))
        return

    print(f"{total} match(es), showing {len(shown)}. Format: name | category | barcode | prices (cheapest first)")
    for p in shown:
        prices = sorted((rp for rp in p["retailer_prices"] if rp.get("price") is not None), key=lambda rp: rp["price"])
        print(f"{p['name']} | {p['category']} | {p['barcode']} | " + ", ".join(price_label(rp) for rp in prices))
    if total > len(shown):
        print(f"... {total - len(shown)} more. Narrow with --grep/--category/--merchant or raise --limit.")


# --------------------------------------------------------------------------- #
# Commands
# --------------------------------------------------------------------------- #

def cmd_categories(data, args):
    print(json.dumps(sorted({p["category"] for p in data["products"]}), ensure_ascii=False))


def cmd_merchants(data, args):
    print(json.dumps(data["merchants"], ensure_ascii=False))


def cmd_count(data, args):
    print(json.dumps({"total": len(data["products"])}))


def cmd_search(data, args):
    products = [p for p in data["products"] if matches_all_words(p["name"], args.query)]
    if args.category:
        category = resolve(args.category, sorted({p["category"] for p in data["products"]}), "category", "categories")
        products = [p for p in products if p["category"] == category]
    merchant = None
    if args.merchant:
        merchant = resolve(args.merchant, data["merchants"], "merchant", "merchants")
        products = [p for p in products if any(rp["merchant_name"] == merchant for rp in p["retailer_prices"])]
    print_products(products, args, merchant)


def cmd_category(data, args):
    category = resolve(args.name, sorted({p["category"] for p in data["products"]}), "category", "categories")
    products = [p for p in data["products"] if p["category"] == category]
    if args.grep:
        products = [p for p in products if matches_all_words(p["name"], args.grep)]
    print_products(products, args)


def cmd_merchant(data, args):
    merchant = resolve(args.name, data["merchants"], "merchant", "merchants")
    products = [p for p in data["products"] if any(rp["merchant_name"] == merchant for rp in p["retailer_prices"])]
    if args.grep:
        products = [p for p in products if matches_all_words(p["name"], args.grep)]
    print_products(products, args, merchant)


def build_parser():
    parser = argparse.ArgumentParser(description="Query Greek supermarket prices.")
    parser.add_argument("--refresh", action="store_true", help="ignore the 60-minute cache and refetch")
    commands = parser.add_subparsers(dest="command", required=True)

    def add_listing_options(p):
        p.add_argument("--limit", type=int, default=25, help="max products to print (default 25)")
        p.add_argument("--sort", choices=["price", "name"], default="price", help="default: cheapest first")
        p.add_argument("--json", action="store_true", help="print raw JSON instead of compact lines")

    commands.add_parser("categories", help="list exact category names").set_defaults(run=cmd_categories)
    commands.add_parser("merchants", help="list exact merchant names").set_defaults(run=cmd_merchants)
    commands.add_parser("count", help="total number of products").set_defaults(run=cmd_count)

    p = commands.add_parser("search", help="find products by name (accent/case-insensitive, all words must match)")
    p.add_argument("query")
    p.add_argument("--category", help="only this category")
    p.add_argument("--merchant", help="only products sold by this merchant")
    add_listing_options(p)
    p.set_defaults(run=cmd_search)

    p = commands.add_parser("category", help="products in a category")
    p.add_argument("name")
    p.add_argument("--grep", help="only products whose name contains these words")
    add_listing_options(p)
    p.set_defaults(run=cmd_category)

    p = commands.add_parser("merchant", help="products sold by a merchant, with that merchant's price")
    p.add_argument("name")
    p.add_argument("--grep", help="only products whose name contains these words")
    add_listing_options(p)
    p.set_defaults(run=cmd_merchant)
    return parser


def main():
    args = build_parser().parse_args()
    try:
        data = load_data(args.refresh)
    except httpx.HTTPError as e:
        sys.exit(f"Could not fetch price data: {e}")
    args.run(data, args)


if __name__ == "__main__":
    main()
