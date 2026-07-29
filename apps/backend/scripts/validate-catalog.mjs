import { readFileSync } from "node:fs";

const catalogUrl = new URL("../data/gramiss-catalog.json", import.meta.url);
const catalog = JSON.parse(readFileSync(catalogUrl, "utf8"));
const products = Array.isArray(catalog.products) ? catalog.products : [];
const errors = [];
const handles = new Set();

function addError(index, message) {
  errors.push(`products[${index}]: ${message}`);
}

function validateStringArray(index, field, value) {
  if (!Array.isArray(value) || value.length === 0) {
    addError(index, `${field} must be a non-empty array.`);
    return;
  }

  const normalized = value.map((item) =>
    typeof item === "string" ? item.trim() : "",
  );

  if (normalized.some((item) => !item)) {
    addError(index, `${field} must contain only non-empty strings.`);
  }

  if (new Set(normalized).size !== normalized.length) {
    addError(index, `${field} must not contain duplicate values.`);
  }
}

if (products.length === 0) {
  errors.push("catalog.products must be a non-empty array.");
}

products.forEach((product, index) => {
  if (!product || typeof product !== "object") {
    addError(index, "product must be an object.");
    return;
  }

  const handle = typeof product.handle === "string" ? product.handle.trim() : "";
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(handle)) {
    addError(index, "handle must use lowercase letters, numbers, and hyphens only.");
  } else if (handles.has(handle)) {
    addError(index, `duplicate handle: ${handle}`);
  } else {
    handles.add(handle);
  }

  for (const field of ["title", "subtitle", "category", "category_key", "material"]) {
    if (typeof product[field] !== "string" || !product[field].trim()) {
      addError(index, `${field} must be a non-empty string.`);
    }
  }

  if (!Number.isInteger(product.price_toman) || product.price_toman <= 0) {
    addError(index, "price_toman must be a positive integer.");
  }

  if (!/^[a-z]{3}$/.test(product.currency_code || "")) {
    addError(index, "currency_code must be a lowercase ISO-style three-letter code.");
  }

  if (product.display_unit !== "تومان") {
    addError(index, "display_unit must remain تومان until the pricing model is finalized.");
  }

  validateStringArray(index, "color_values", product.color_values);
  validateStringArray(index, "size_values", product.size_values);

  if (typeof product.in_stock !== "boolean") {
    addError(index, "in_stock must be boolean.");
  }

  if (typeof product.image !== "string" || !product.image.startsWith("/assets/")) {
    addError(index, "image must reference a storefront asset under /assets/.");
  }

  if (!product.metadata || typeof product.metadata !== "object") {
    addError(index, "metadata must be an object.");
  }
});

if (errors.length > 0) {
  console.error("Gramiss catalog validation failed:\n");
  for (const error of errors) {
    console.error(`- ${error}`);
  }
  process.exit(1);
}

const categories = [...new Set(products.map((product) => product.category_key))];
console.log(
  `Gramiss catalog valid: ${products.length} products across ${categories.length} categories.`,
);
