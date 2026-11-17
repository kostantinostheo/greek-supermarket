import math
import time
from datetime import datetime, timezone
from functools import cmp_to_key
from typing import Annotated

import httpx
from fastapi import APIRouter, HTTPException, Query

from consts.endpoints import ENDPOINT
from transformer import transform_data
from utils.crypto import decrypt
from utils.customize_categories import flatten_categories, get_categories_list
from utils.helper import normalize_text

router = APIRouter()


def get_dynamic_url():
    cid = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"{decrypt(ENDPOINT['BASE']['URL'])}{cid}"


async def fetch_data():
    url = get_dynamic_url()
    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
        response = await client.get(url)
    if not response.is_success:
        raise Exception(f"Fetch failed: {response.status_code}")
    data = response.json()
    return ((data.get("context") or {}).get("MAPP_PRODUCTS") or {}).get("result") or {}


cache = {
    "data": None,
    "last_fetched": None,
}


async def get_processed_products():
    now = time.time() * 1000
    # Refresh cache only if empty or older than 60 minutes
    if cache["data"] is None or (now - cache["last_fetched"] > 60 * 60 * 1000):
        print("Cache miss. Fetching fresh data...")
        raw_result = await fetch_data()
        category_map = flatten_categories(raw_result.get("categories"))
        cache["data"] = transform_data(raw_result, category_map)
        cache["last_fetched"] = now
    return cache["data"]


@router.get(
    "/products/length",
    summary="Retrieve the total number of products available in the dataset.",
    responses={
        200: {"description": "Total number of products."},
        500: {"description": "Server error while fetching products."},
    },
)
async def products_length():
    try:
        products = await get_processed_products()
        return {"total": len(products)}
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch and process products")


@router.get(
    "/products",
    summary="Retrieve a paginated list of products.",
    responses={
        200: {"description": "A paginated list of products."},
        500: {"description": "Server error while fetching products."},
    },
)
async def get_products(
    page: Annotated[int, Query(description="Page number.")] = 1,
    limit: Annotated[int, Query(description="Number of products per page.")] = 20,
    order_by: Annotated[str, Query(alias="orderBy")] = "name",  # Default to 'name'
    order: str = "asc",  # Default to 'asc'
):
    try:
        products = await get_processed_products()

        # Query params
        page = page or 1
        limit = limit or 20

        # Sorting logic
        order = -1 if order == "desc" else 1

        def compare(a, b):
            try:
                if a.get(order_by) < b.get(order_by):
                    return -1 * order
                if a.get(order_by) > b.get(order_by):
                    return 1 * order
            except TypeError:
                pass
            return 0

        products.sort(key=cmp_to_key(compare))
        # Pagination calculations
        start_index = (page - 1) * limit
        end_index = start_index + limit

        # Paginated data
        paginated_products = products[start_index:end_index]

        return {
            "page": page,
            "limit": limit,
            "totalProducts": len(products),
            "totalPages": math.ceil(len(products) / limit),
            "data": paginated_products,
        }

    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch and process products")


@router.get(
    "/products/search",
    summary="Search products by name.",
    description=(
        "Performs a case-insensitive and accent-insensitive search.\n"
        "Supports multi-word queries."
    ),
    responses={
        200: {"description": "A list of matching products."},
        400: {"description": "Search query is required."},
        500: {"description": "Server error while searching products."},
    },
)
async def search_products(
    q: Annotated[str, Query(description="Search query (e.g. γαλα δελτα)")] = "",
):
    try:
        products = await get_processed_products()

        query = normalize_text(q)

        if not query:
            raise HTTPException(status_code=400, detail="Search query is required")

        results = [
            product for product in products
            if query in normalize_text(product["name"])
        ]

        return {
            "count": len(results),
            "data": results,
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to search products")


@router.get(
    "/products/category/{category_name}",
    summary="Retrieve a list of products filtered by a specific category.",
    responses={
        200: {"description": "A list of products belonging to the specified category."},
        500: {"description": "Server error while filtering products by category."},
    },
)
async def get_products_by_category(category_name: str):
    try:
        products = await get_processed_products()
        filtered = [product for product in products if product["category"] == category_name]
        return {
            "category": category_name,
            "count": len(filtered),
            "results": filtered,
        }
    except Exception:
        raise HTTPException(status_code=500, detail="Filtering by category failed")


@router.get(
    "/categories",
    summary="Retrieve a list of all product categories available in the dataset.",
    responses={
        200: {"description": "A list of product categories."},
        500: {"description": "Server error while fetching categories."},
    },
)
async def get_categories():
    try:
        products = await get_processed_products()
        categories = get_categories_list(products)
        return categories
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch categories")


@router.get(
    "/merchants",
    summary="Retrieve a list of all merchants available in the dataset.",
    responses={
        200: {"description": "A list of merchants."},
        500: {"description": "Server error while fetching merchants."},
    },
)
async def get_merchants():
    try:
        products = await fetch_data()
        return sorted(m["name"] for m in products["merchants"])
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch merchants")


@router.get(
    "/products/merchant/{merchant_name}",
    summary="Retrieve a list of products filtered by a specific merchant.",
    responses={
        200: {"description": "A list of products sold by the specified merchant."},
        500: {"description": "Server error while filtering products by merchant."},
    },
)
async def get_products_by_merchant(merchant_name: str):
    try:
        products = await get_processed_products()

        def filter_by_merchant(products, merchant_name):
            filtered = [
                product for product in products
                if any(rp["merchant_name"] == merchant_name for rp in product["retailer_prices"])
            ]

            return {
                "merchant": merchant_name,
                "count": len(filtered),
                "results": [
                    {
                        "name": product["name"],
                        "category": product["category"],
                        "price": next(
                            (rp["price"] for rp in product["retailer_prices"]
                             if rp["merchant_name"] == merchant_name),
                            None,
                        ),
                    }
                    for product in filtered
                ],
            }

        return filter_by_merchant(products, merchant_name)
    except Exception:
        raise HTTPException(status_code=500, detail="Filtering by merchant failed")
