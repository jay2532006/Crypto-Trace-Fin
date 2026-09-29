export function formatInr(value: number): string {
  return `₹${value.toLocaleString("en-IN")}`;
}

export function formatDateTime(value: string): string {
  return value.replace("T", " ").slice(0, 19);
}

export function formatTechnicalId(value: string, head = 10, tail = 6): string {
  if (value.length <= head + tail + 3) return value;
  return `${value.slice(0, head)}...${value.slice(-tail)}`;
}

export function formatWallet(value: string): string {
  return formatTechnicalId(value, 12, 8);
}

export function formatHops(value: number): string {
  return `${value} ${value === 1 ? "hop" : "hops"}`;
}
