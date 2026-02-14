import { useEffect, useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import api from '@/lib/api';
import { formatDate } from '@/lib/utils';
import type { TimeSeriesData } from '@/types';

interface TemperatureChartProps {
  locationId?: number;
  startDate?: string;
  endDate?: string;
}

export default function TemperatureChart({
  locationId,
  startDate,
  endDate,
}: TemperatureChartProps) {
  const [data, setData] = useState<TimeSeriesData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, [locationId, startDate, endDate]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      const params: any = {};
      if (locationId) params.location = locationId;
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;

      const timeSeriesData = await api.getTemperatureTimeSeries(params);
      setData(timeSeriesData);
    } catch (err) {
      setError('Failed to load temperature data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-ocean-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">{error}</p>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-yellow-800">No temperature data available for the selected filters.</p>
      </div>
    );
  }

  const chartData = data.map((item) => ({
    timestamp: formatDate(item.timestamp, 'MMM dd HH:mm'),
    temperature: item.value,
  }));

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-semibold text-ocean-900 mb-4">
        Temperature Over Time
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="timestamp"
            tick={{ fontSize: 12 }}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis
            label={{ value: 'Temperature (°C)', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              border: '1px solid #ccc',
              borderRadius: '4px',
            }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="temperature"
            stroke="#0284c7"
            strokeWidth={2}
            dot={{ r: 3 }}
            activeDot={{ r: 5 }}
            name="Temperature (°C)"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
