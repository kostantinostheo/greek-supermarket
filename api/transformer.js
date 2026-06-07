import { normalizeCategory } from "./utils/normalizeCategories.js";

export const transformData = (result, categoryMap) => {
  const merchantMap = Object.fromEntries(
    (result.merchants || []).map(m => [m.merchant_uuid, m.name || ""])
  );

  return (result.products || []).map(product => ({
    name: (product.name || "").toLowerCase(),
    barcode: product.barcode,
    category:
      normalizeCategory(
        categoryMap[product.category?.[0]] ||
        String(product.category?.[0] || "")
      ) || "Λοιπά",
    image: product.image,
    retailer_prices: (product.prices || []).map(p => ({
      merchant_name:
        merchantMap[p.merchant_uuid] || `Merchant ${p.merchant_uuid}`,
      price: p.price,
      price_normalized: p.price_normalized,
    })),
  }));
};