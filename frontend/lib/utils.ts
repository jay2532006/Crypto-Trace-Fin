import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
export function formatAddress(value: string, ...args: any[]): string {
  if (!value) return "";
  return value.length > 10 ? value.slice(0, 6) + '...' + value.slice(-4) : value;
}
export function formatCrypto(value: number, ...args: any[]): string {
  return value ? value.toFixed(4) : "0.0000";
}
export function formatINR(value: number, ...args: any[]): string {
  return ",1" + (value ? value.toLocaleString("en-IN") : "0");
}
export function formatCurrency(value: number, ...args: any[]): string {
  return formatINR(value, ...args);
}
export function formatUSD(value: number, ...args: any[]): string {
  return "$" + (value ? value.toLocaleString("en-US") : "0");
}
export function formatDateTime(value: string, ...args: any[]): string {
  return value ? value.replace("T", " ").slice(0, 19) : "";
}
