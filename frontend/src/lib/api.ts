/**
 * API client for Ocean Data Dashboard backend
 */
import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  ApiResponse,
  DataSource,
  Location,
  TemperatureObservation,
  SalinityObservation,
  CurrentObservation,
  IngestionLog,
  TimeSeriesData,
  StatisticsData,
} from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add auth token if available
        const token = localStorage.getItem('token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        // Handle errors globally
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  // Data Sources
  async getDataSources(): Promise<DataSource[]> {
    const response = await this.client.get<ApiResponse<DataSource>>('/sources/');
    return response.data.results;
  }

  async getDataSource(id: number): Promise<DataSource> {
    const response = await this.client.get<DataSource>(`/sources/${id}/`);
    return response.data;
  }

  // Locations
  async getLocations(params?: { region?: string }): Promise<Location[]> {
    const response = await this.client.get<ApiResponse<Location>>('/locations/', { params });
    return response.data.results;
  }

  async getLocation(id: number): Promise<Location> {
    const response = await this.client.get<Location>(`/locations/${id}/`);
    return response.data;
  }

  // Temperature Observations
  async getTemperatureObservations(params?: {
    location?: number;
    source?: number;
    start_date?: string;
    end_date?: string;
    page?: number;
  }): Promise<ApiResponse<TemperatureObservation>> {
    const response = await this.client.get<ApiResponse<TemperatureObservation>>(
      '/temperature/',
      { params }
    );
    return response.data;
  }

  async getTemperatureTimeSeries(params?: {
    location?: number;
    start_date?: string;
    end_date?: string;
  }): Promise<TimeSeriesData[]> {
    const response = await this.client.get<TimeSeriesData[]>(
      '/temperature/time_series/',
      { params }
    );
    return response.data;
  }

  async getTemperatureStatistics(params?: {
    location?: number;
    start_date?: string;
    end_date?: string;
  }): Promise<StatisticsData> {
    const response = await this.client.get<StatisticsData>(
      '/temperature/statistics/',
      { params }
    );
    return response.data;
  }

  // Salinity Observations
  async getSalinityObservations(params?: {
    location?: number;
    source?: number;
    start_date?: string;
    end_date?: string;
    page?: number;
  }): Promise<ApiResponse<SalinityObservation>> {
    const response = await this.client.get<ApiResponse<SalinityObservation>>(
      '/salinity/',
      { params }
    );
    return response.data;
  }

  async getSalinityTimeSeries(params?: {
    location?: number;
    start_date?: string;
    end_date?: string;
  }): Promise<TimeSeriesData[]> {
    const response = await this.client.get<TimeSeriesData[]>(
      '/salinity/time_series/',
      { params }
    );
    return response.data;
  }

  // Current Observations
  async getCurrentObservations(params?: {
    location?: number;
    source?: number;
    start_date?: string;
    end_date?: string;
    page?: number;
  }): Promise<ApiResponse<CurrentObservation>> {
    const response = await this.client.get<ApiResponse<CurrentObservation>>(
      '/currents/',
      { params }
    );
    return response.data;
  }

  async getCurrentTimeSeries(params?: {
    location?: number;
    start_date?: string;
    end_date?: string;
  }): Promise<TimeSeriesData[]> {
    const response = await this.client.get<TimeSeriesData[]>(
      '/currents/time_series/',
      { params }
    );
    return response.data;
  }

  // Ingestion Logs
  async getIngestionLogs(params?: {
    source?: number;
    status?: string;
    page?: number;
  }): Promise<ApiResponse<IngestionLog>> {
    const response = await this.client.get<ApiResponse<IngestionLog>>(
      '/ingestion-logs/',
      { params }
    );
    return response.data;
  }

  async getIngestionLogsSummary(): Promise<any> {
    const response = await this.client.get('/ingestion-logs/summary/');
    return response.data;
  }
}

// Export singleton instance
export const api = new ApiClient();
export default api;
