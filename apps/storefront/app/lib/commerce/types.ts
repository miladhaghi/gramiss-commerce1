export type CommerceMode = "demo" | "medusa";

export type CommerceMoney = {
  amount: number;
  currencyCode: string;
};

export type CommerceProductOptionValue = {
  id: string;
  value: string;
};

export type CommerceProductOption = {
  id: string;
  title: string;
  values: CommerceProductOptionValue[];
};

export type CommerceProductVariant = {
  id: string;
  title: string;
  sku?: string | null;
  inventoryQuantity?: number | null;
  calculatedPrice?: CommerceMoney | null;
  options: Record<string, string>;
};

export type CommerceProduct = {
  id: string;
  handle: string;
  title: string;
  subtitle?: string | null;
  description?: string | null;
  thumbnail?: string | null;
  images: string[];
  collectionId?: string | null;
  categoryIds: string[];
  tags: string[];
  options: CommerceProductOption[];
  variants: CommerceProductVariant[];
  metadata?: Record<string, unknown> | null;
};

export type CommerceCartLine = {
  id: string;
  productId: string;
  variantId: string;
  title: string;
  quantity: number;
  unitPrice: CommerceMoney;
  thumbnail?: string | null;
  options: Record<string, string>;
};

export type CommerceCart = {
  id: string;
  regionId: string;
  items: CommerceCartLine[];
  subtotal: CommerceMoney;
  shippingTotal: CommerceMoney;
  discountTotal: CommerceMoney;
  taxTotal: CommerceMoney;
  total: CommerceMoney;
};
