export type Product = {
  id: string;
  badge: string;
  category: string;
  name: string;
  english: string;
  price: string;
  image: string;
  productHref?: string;
  description?: string;
  material?: string;
  color?: string;
  colors?: readonly string[];
  sizes?: readonly string[];
  tags?: readonly string[];
};
