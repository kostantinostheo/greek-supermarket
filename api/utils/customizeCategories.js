/**
 * Recursively extracts all category UUIDs into a flat map.
 */
export const flattenCategories = (cats, mapping = {}) => {
    if (!cats) return mapping;
    cats.forEach(cat => {
        if (cat.uuid && cat.name) {
            mapping[cat.uuid] = cat.name.toLowerCase();
        }
        if (cat.sub_categories) flattenCategories(cat.sub_categories, mapping);
        if (cat.sub_sub_categories) flattenCategories(cat.sub_sub_categories, mapping);
    });
    return mapping;
};

/**
 * Filter products by category name (case-insensitive).
 */
export const getProductsByCategoryName = (products, categoryName) => {
    const searchName = categoryName.toLowerCase();
    return products.filter(product => 
        product.categories.some(cat => cat === searchName)
    );
};

// Utility to get unique sorted list of all categories from products
export const getCategoriesList = (products) => {
    const categorySet = new Set();
    products.forEach(product => {
        categorySet.add(product.category);
    });
    return Array.from(categorySet).sort();
}