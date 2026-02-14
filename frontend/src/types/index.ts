/**
 * Type definitions for Ocean Data Dashboard
 */

export interface DataSource {
  id: number;
  name: string;
  url: string;
  description: string;
  is_active: boolean;
  last_fetch: string | null;
  created_at: string;
  updated_at: string;
}

export interface Location {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  depth_meters: number | null;
  region: string;
  created_at: string;
}

export interface TemperatureObservation {
  id: number;
  location: number;
  location_name: string;
  source: number;
  source_name: string;
  timestamp: string;
  temperature_celsius: number;
  quality_flag: string;
  created_at: string;
}

export interface SalinityObservation {
  id: number;
  location: number;
  location_name: string;
  source: number;
  source_name: string;
  timestamp: string;
  salinity_psu: number;
  quality_flag: string;
  created_at: string;
}

export interface CurrentObservation {
  id: number;
  location: number;
  location_name: string;
  source: number;
  source_name: string;
  timestamp: string;
  speed_ms: number;
  direction_degrees: number;
  u_component: number | null;
  v_component: number | null;
  quality_flag: string;
  created_at: string;
}

export interface IngestionLog {
  id: number;
  source: number;
  source_name: string;
  status: 'pending' | 'running' | 'success' | 'failed';
  started_at: string;
  completed_at: string | null;
  duration_seconds: number | null;
  records_fetched: number;
  records_inserted: number;
  error_message: string;
  task_id: string;
}

export interface TimeSeriesData {
  timestamp: string;
  value: number;
  location?: string;
  variable?: string;
}

export interface DateRange {
  start: Date;
  end: Date;
}

export interface ChartData {
  time: string;
  value: number;
  location?: string;
}

export interface ApiResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface StatisticsData {
  avg_temperature?: number;
  min_temperature?: number;
  max_temperature?: number;
  total_observations: number;
}
