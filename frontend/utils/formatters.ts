export function formatInr(value?: number | null): string {
  if (value === undefined || value === null || isNaN(Number(value))) return "₹0";
  return `₹${Number(value).toLocaleString("en-IN")}`;
}

export function formatDateTime(value?: string | null): string {
  if (!value) return "";
  return String(value).replace("T", " ").slice(0, 19);
}

export function formatTechnicalId(value?: string | null, head = 10, tail = 6): string {
  if (!value) return "";
  const str = String(value);
  if (str.length <= head + tail + 3) return str;
  return `${str.slice(0, head)}...${str.slice(-tail)}`;
}

export function formatWallet(value?: string | null): string {
  if (!value) return "";
  return formatTechnicalId(value, 12, 8);
}

export function formatHops(value?: number | null): string {
  if (value === undefined || value === null) return "0 hops";
  return `${value} ${value === 1 ? "hop" : "hops"}`;
}
