import httpx

BASE_URL = "http://localhost:8000/api/v1"


def get_all_products_func(page: int = 1, limit: int = 20) -> list:
    """Function that fetches all products from the API with pagination. 

    Args:
        page (int, optional): The page number to retrieve. Defaults to 1.
        limit (int, optional): The number of products to retrieve per page. Defaults to 20.

    Returns:
        list: A list of products retrieved from the API.
    """
    response = httpx.get(f"{BASE_URL}/products?page={page}&limit={limit}", timeout=30)
    response.raise_for_status()
    return response.json()


def get_number_of_products_func() -> int:
    """Fetch the total number of products available in the Greek Supermarket.

    Returns:
        int: The total number of products available in the Greek Supermarket.
    """
    response = httpx.get(f"{BASE_URL}/products/length", timeout=30)
    response.raise_for_status()
    return response.json()


def get_merchants_func() -> list:
    """Fetch a list of all merchant names from the API.

    Returns:
        list: A list of all merchant names available in the Greek Supermarket.
    """
    response = httpx.get(f"{BASE_URL}/merchants", timeout=30)
    response.raise_for_status()
    return response.json()



def get_categories_func() -> list:
    """Fetch a list of all product categories from the API.

    Returns:
        list: A list of all product categories available in the Greek Supermarket.
    """
    response = httpx.get(f"{BASE_URL}/categories", timeout=30)
    response.raise_for_status()
    return response.json()


def get_products_by_merchant_func(merchant_name: str) -> dict:
    """Fetch the products of a specific merchant from the API.

    Args:
        merchant_name (str): The exact merchant name (as returned by get_merchants).

    Returns:
        dict: A dictionary containing the products sold by the specified merchant, including product name, price, and category.
    """
    response = httpx.get(f"{BASE_URL}/products/merchant/{merchant_name}", timeout=30)
    response.raise_for_status()
    return response.json()

def get_products_by_category_func(category_name: str) -> dict:
    """Fetch the products of a specific category from the API.

    Args:
        category_name (str): The exact category name (as returned by get_categories).

    Returns:
        dict: A dictionary containing the products included in the specified category, including product name, price, and merchant name.
    """
    res = httpx.get(f"{BASE_URL}/products/category/{category_name}", timeout=30)
    res.raise_for_status()
    return res.json()