import { transformData } from '../transformer.js';
import { flattenCategories, getCategoriesList } from '../utils/customizeCategories.js';
import express from 'express';
import { decrypt } from '../utils/crypto.js';

import ENDPOINT from '../consts/endpoints.js';
import { normalizeText } from '../utils/helper.js';

const router = express.Router();

const getDynamicUrl = () => {
    const cid = new Date().toISOString().replace(/[-:T.Z]/g, "").slice(0, 14);
    return `${decrypt(ENDPOINT.BASE.URL)}${cid}`;
};

export const fetchData = async () => {
    const url = getDynamicUrl();
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Fetch failed: ${response.status}`);
    const data = await response.json();
    return data?.context?.MAPP_PRODUCTS?.result || {};
};

let cache = {
    data: null,
    lastFetched: null
};

const getProcessedProducts = async () => {
    const now = Date.now();
    // Refresh cache only if empty or older than 60 minutes
    if (!cache.data || (now - cache.lastFetched > 60 * 60 * 1000)) {
        console.log("Cache miss. Fetching fresh data...");
        const rawResult = await fetchData();
        const categoryMap = flattenCategories(rawResult.categories);
        cache.data = transformData(rawResult, categoryMap);
        cache.lastFetched = now;
    }
    return cache.data;
};

/**
 * @swagger
 * /products/length:
 *   get:
 *     summary: Retrieve the total number of products available in the dataset.
 *     responses:
 *       200:
 *         description: Total number of products.
 *       500:
 *         description: Server error while fetching products.
 */
router.get('/products/length', async (req, res) => {
    try {
        const products = await getProcessedProducts();
        res.json({ total: products.length });
    } catch (error) {
        res.status(500).json({
            error: "Failed to fetch and process products"
        });
    }
});

/**
 * @swagger
 * /products:
 *   get:
 *     summary: Retrieve a paginated list of products.
 *     parameters:
 *       - in: query
 *         name: page
 *         schema:
 *           type: integer
 *           default: 1
 *         description: Page number.
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           default: 20
 *         description: Number of products per page.
 *     responses:
 *       200:
 *         description: A paginated list of products.
 *       500:
 *         description: Server error while fetching products.
 */
router.get('/products', async (req, res) => {
    try {
        const products = await getProcessedProducts();

        // Query params
        const page = parseInt(req.query.page) || 1;
        const limit = parseInt(req.query.limit) || 20;
        
        // Sorting logic
        const orderBy = req.query.orderBy || 'name'; // Default to 'name'
        const order = req.query.order === 'desc' ? -1 : 1; // Default to 'asc'

        products.sort((a, b) => {
            if (a[orderBy] < b[orderBy]) return -1 * order;
            if (a[orderBy] > b[orderBy]) return 1 * order;
            return 0;
        });
        // Pagination calculations
        const startIndex = (page - 1) * limit;
        const endIndex = startIndex + limit;

        // Paginated data
        const paginatedProducts = products.slice(startIndex, endIndex);

        res.json({
            page,
            limit,
            totalProducts: products.length,
            totalPages: Math.ceil(products.length / limit),
            data: paginatedProducts
        });

    } catch (error) {
        res.status(500).json({
            error: "Failed to fetch and process products"
        });
    }
});

/**
 * @swagger
 * /products/search:
 *   get:
 *     summary: Search products by name.
 *     description: |
 *       Performs a case-insensitive and accent-insensitive search.
 *       Supports multi-word queries.
 *     parameters:
 *       - in: query
 *         name: q
 *         required: true
 *         schema:
 *           type: string
 *         description: Search query (e.g. γαλα δελτα)
 *     responses:
 *       200:
 *         description: A list of matching products.
 *       400:
 *         description: Search query is required.
 *       500:
 *         description: Server error while searching products.
 */
router.get('/products/search', async (req, res) => {
    try {
        const products = await getProcessedProducts();

        const query = normalizeText(req.query.q);

        if (!query) {
            return res.status(400).json({
                error: "Search query is required"
            });
        }

        const results = products.filter(product => {
            return normalizeText(product.name).includes(query);
        });

        res.json({
            count: results.length,
            data: results
        });

    } catch (error) {
        res.status(500).json({
            error: "Failed to search products"
        });
    }
});

/**
 * @swagger
 * /products/category/{category_name}:
 *   get:
 *     summary: Retrieve a list of products filtered by a specific category.
 *     parameters:
 *       - in: path
 *         name: category_name
 *         required: true
 *         schema:
 *           type: string
 *         description: The name of the category to filter products by.
 *     responses:
 *       200:
 *         description: A list of products belonging to the specified category.
 *       500:
 *         description: Server error while filtering products by category.
 */
router.get('/products/category/:category_name', async (req, res) => {
    try {
        const categoryName = req.params.category_name;
        const products = await getProcessedProducts();
        const filtered = products.filter(product => product.category === categoryName);
        res.json({
            category: categoryName,
            count: filtered.length,
            results: filtered
        });
    } catch (error) {
        res.status(500).json({ error: "Filtering by category failed" });
    }
});

/**
* @swagger
* /categories:
*   get:
*     summary: Retrieve a list of all product categories available in the dataset.
*     responses:
*       200:
*         description: A list of product categories.
*       500:
*         description: Server error while fetching categories.
*/
router.get('/categories', async (req, res) => {
    try {
        const products = await getProcessedProducts();
        const categories = getCategoriesList(products);
        res.json(categories);
    } catch (error) {
        res.status(500).json({ error: "Failed to fetch categories" });
    }
});

/**
 * @swagger
 * /merchants:
 *  get:
 *   summary: Retrieve a list of all merchants available in the dataset.
 *   responses:
 *      200:
 *          description: A list of merchants.
 *      500:
 *          description: Server error while fetching merchants.
 */
router.get('/merchants', async (req, res) => {
    try {
        const products = await fetchData();
        res.json(products.merchants.map(m => m.name).sort());
    } catch (error) {
        res.status(500).json({ error: "Failed to fetch merchants" });
    }
});

/**
 * @swagger
 * /products/merchant/{merchant_name}:
 *   get:
 *     summary: Retrieve a list of products filtered by a specific merchant.
 *     parameters:
 *       - in: path
 *         name: merchant_name
 *         required: true
 *         schema:
 *           type: string
 *         description: The name of the merchant to filter products by.
 *     responses:
 *       200:
 *         description: A list of products sold by the specified merchant.
 *       500:
 *         description: Server error while filtering products by merchant.
 */
router.get('/products/merchant/:merchant_name', async (req, res) => {
    try {
        const merchantName = req.params.merchant_name;
        const products = await getProcessedProducts();
        const filterByMerchant = (products, merchantName) => {
            const filtered = products.filter(product => 
              product.retailer_prices.some(rp => rp.merchant_name === merchantName)
            );
          
            return {
              merchant: merchantName,
              count: filtered.length,
              results: filtered.map(product => ({
                name: product.name,
                category: product.category,
                price: product.retailer_prices.find(rp => rp.merchant_name === merchantName)?.price
              }))
            };
          };
        const filtered = filterByMerchant(products, merchantName);
        
        res.json(filtered);
    } catch (error) {
        res.status(500).json({ error: "Filtering by merchant failed" });
    }
});

export default router;