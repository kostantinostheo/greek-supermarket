def flatten_categories(cats, mapping=None):
    """
    Recursively extracts all category UUIDs into a flat map.
    """
    if mapping is None:
        mapping = {}
    if not cats:
        return mapping
    for cat in cats:
        if cat.get("uuid") and cat.get("name"):
            mapping[cat["uuid"]] = cat["name"].lower()
        if cat.get("sub_categories"):
            flatten_categories(cat["sub_categories"], mapping)
        if cat.get("sub_sub_categories"):
            flatten_categories(cat["sub_sub_categories"], mapping)
    return mapping


def get_products_by_category_name(products, category_name):
    """
    Filter products by category name (case-insensitive).
    """
    search_name = category_name.lower()
    return [
        product for product in products
        if any(cat == search_name for cat in product["categories"])
    ]


def get_categories_list(products):
    """Utility to get unique sorted list of all categories from products."""
    category_set = set()
    for product in products:
        category_set.add(product["category"])
    return sorted(category_set)
