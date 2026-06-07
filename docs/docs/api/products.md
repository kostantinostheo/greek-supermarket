---
sidebar_position: 1
---

# Products

## Get All Products

Retrieve a paginated list of products.

```
GET /products
```

### Query Parameters

| Parameter | Type    | Default | Description              |
|-----------|---------|---------|--------------------------|
| `page`    | integer | 1       | Page number              |
| `limit`   | integer | 20      | Products per page        |
| `orderBy` | string  | name    | Field to sort by         |
| `order`   | string  | asc     | Sort order (`asc`/`desc`)|

### Response

```json
{
  "page": 1,
  "limit": 20,
  "totalProducts": 1000,
  "totalPages": 100,
  "data": [
    {
      "name": "product name",
      "barcode": "barcode",
      "category": "product category",
      "image": "product image",
      "retailer_prices": [
        {
          "merchant_name": "merchant name",
          "price": 10,
          "price_normalized": 10
        },
      ]
    }
  ]
}
```

---

## Search Products

Search products by name (case-insensitive, accent-insensitive).

```
GET /products/search?q=your+query
```

### Query Parameters

| Parameter | Type   | Required | Description   |
|-----------|--------|----------|---------------|
| `q`       | string | Yes      | Search query  |

### Response

```json
{
  "count": 100,
  "data": [...]
}
```

---

## Products by Category

```
GET /products/category/:category_name
```

### Response

```json
{
  "category": "category name",
  "count": 100,
  "results": [...]
}
```

---

## Products by Merchant

```
GET /products/merchant/:merchant_name
```

### Response

```json
{
  "merchant": "merchant name",
  "count": 100,
  "results": [
    {
      "name": "product name",
      "category": "category",
      "price": 10
    }
  ]
}
```
