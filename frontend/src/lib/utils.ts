/**
 * Utility functions for Ocean Data Dashboard
 */
import { format, parseISO, subDays } from 'date-fns';
import { clsx, type ClassValue } from 'clsx';

/**
 * Merge class names
 */
export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

/**
 * Format date for display
 */
export function formatDate(date: string | Date, formatStr: string = 'PPpp'): string {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  return format(dateObj, formatStr);
}

/**
 * Format date for API (ISO 8601)
 */
export function formatDateForApi(date: Date): string {
  return date.toISOString();
}

/**
 * Get date range for last N days
 */
export function getLastNDays(days: number): { start: Date; end: Date } {
  const end = new Date();
  const start = subDays(end, days);
  return { start, end };
}

/**
 * Format temperature for display
 */
export function formatTemperature(celsius: number, decimals: number = 1): string {
  return `${celsius.toFixed(decimals)}°C`;
}

/**
 * Format salinity for display
 */
export function formatSalinity(psu: number, decimals: number = 2): string {
  return `${psu.toFixed(decimals)} PSU`;
}

/**
 * Format current speed for display
 */
export function formatCurrentSpeed(ms: number, decimals: number = 2): string {
  return `${ms.toFixed(decimals)} m/s`;
}

/**
 * Format direction in degrees
 */
export function formatDirection(degrees: number): string {
  const directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
  const index = Math.round(((degrees % 360) / 45)) % 8;
  return `${degrees.toFixed(0)}° ${directions[index]}`;
}

/**
 * Debounce function
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Get color for data quality flag
 */
export function getQualityFlagColor(flag: string): string {
  const flagLower = flag.toLowerCase();
  if (flagLower.includes('good') || flagLower === '1') return 'text-green-600';
  if (flagLower.includes('suspect') || flagLower === '2') return 'text-yellow-600';
  if (flagLower.includes('bad') || flagLower === '3') return 'text-red-600';
  return 'text-gray-600';
}

/**
 * Calculate statistics from array of numbers
 */
export function calculateStats(values: number[]): {
  min: number;
  max: number;
  avg: number;
  median: number;
} {
  const sorted = [...values].sort((a, b) => a - b);
  const sum = values.reduce((acc, val) => acc + val, 0);
  
  return {
    min: Math.min(...values),
    max: Math.max(...values),
    avg: sum / values.length,
    median: sorted[Math.floor(sorted.length / 2)],
  };
}

/**
 * Format large numbers with K, M, B suffix
 */
export function formatNumber(num: number): string {
  if (num >= 1e9) return `${(num / 1e9).toFixed(1)}B`;
  if (num >= 1e6) return `${(num / 1e6).toFixed(1)}M`;
  if (num >= 1e3) return `${(num / 1e3).toFixed(1)}K`;
  return num.toString();
}

/**
 * Check if string is valid date
 */
export function isValidDate(dateString: string): boolean {
  const date = new Date(dateString);
  return !isNaN(date.getTime());
}
