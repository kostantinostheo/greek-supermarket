from mcp.server.fastmcp import FastMCP

from functions import *

mcp = FastMCP("Greek Supermarket Tools")

@mcp.tool()
def get_all_products(page: int = 1, limit: int = 20) -> list:
    """Get all products available in the Greek Supermarket.ss
    Args:
        page: The page number to retrieve (starting from 1).
        limit: The number of products to retrieve per page.
    """
    return get_all_products_func(page, limit)

@mcp.tool()
def get_number_of_products() -> int:
    """Get the total number of products available in the Greek Supermarket."""
    return get_number_of_products_func()

@mcp.tool()
def get_merchants() -> list:
    """Get a list of all merchant names."""
    return get_merchants_func()

@mcp.tool()
def get_categories() -> list:
    """Get a list of all product categories."""
    return get_categories_func()





@mcp.tool()
def get_products_by_merchant(merchant_name: str) -> dict:
    """Get products sold by a specific merchant.

    Args:
        merchant_name: The exact merchant name (as returned by get_merchants).
    """
    return get_products_by_merchant_func(merchant_name)

@mcp.tool()
def get_products_by_category(category_name: str) -> dict:
    """
    Get all the products that are included to a specific category.
    Create a dynamic table with the following columns: product name, price, merchant name.
    Args:
        category_name: The exact category name (as returned by get_categories).
    """
    return get_products_by_category_func(category_name)



if __name__ == "__main__":
    mcp.run()