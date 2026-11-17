from utils.normalize_categories import normalize_category


def _first(value):
    # product.category?.[0]
    return value[0] if value else None


def transform_data(result, category_map):
    merchant_map = {
        m.get("merchant_uuid"): m.get("name") or ""
        for m in (result.get("merchants") or [])
    }

    products = []
    for product in (result.get("products") or []):
        first_category = _first(product.get("category"))
        products.append({
            "name": (product.get("name") or "").lower(),
            "barcode": product.get("barcode"),
            "category":
                normalize_category(
                    category_map.get(first_category)
                    or str(first_category or "")
                ) or "Λοιπά",
            "image": product.get("image"),
            "retailer_prices": [
                {
                    "merchant_name":
                        merchant_map.get(p.get("merchant_uuid")) or f"Merchant {p.get('merchant_uuid')}",
                    "price": p.get("price"),
                    "price_normalized": p.get("price_normalized"),
                }
                for p in (product.get("prices") or [])
            ],
        })
    return products
