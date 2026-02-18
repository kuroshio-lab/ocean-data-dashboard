import Head from 'next/head';
import { useEffect, useState } from 'react';
import api from '@/lib/api';
import TemperatureChart from '@/components/TemperatureChart';
import type { Location, DataSource } from '@/types';

export default function Home() {
  const [locations, setLocations] = useState<Location[]>([]);
  const [sources, setSources] = useState<DataSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedLocation, setSelectedLocation] = useState<number | undefined>(undefined);
  const [hasTemperatureData, setHasTemperatureData] = useState(false);

  // Calculate default date range (last 7 days)
  const today = new Date().toISOString().split('T')[0];
  const lastWeek = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
  const [startDate, setStartDate] = useState(lastWeek);
  const [endDate, setEndDate] = useState(today);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [locationsData, sourcesData, tempData] = await Promise.all([
        api.getLocations(),
        api.getDataSources(),
        api.getTemperatureObservations({ page: 1 }).catch(() => ({ count: 0 })),
      ]);
      setLocations(locationsData);
      setSources(sourcesData);
      setHasTemperatureData(tempData.count > 0);

      // Auto-select first location if available
      if (locationsData.length > 0 && !selectedLocation) {
        setSelectedLocation(locationsData[0].id);
      }
    } catch (err) {
      setError('Failed to load data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Head>
        <title>Ocean Data Dashboard</title>
        <meta name="description" content="Real-time oceanographic data visualization" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="min-h-screen bg-gradient-to-b from-ocean-50 to-ocean-100">
        <div className="container mx-auto px-4 py-8">
          <header className="mb-8 text-center">
            <h1 className="text-4xl font-bold text-ocean-900 mb-2">
              🌊 Ocean Data Dashboard
            </h1>
            <p className="text-lg text-ocean-700">
              Real-time oceanographic data from trusted scientific sources
            </p>
          </header>

          {loading && (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-ocean-600"></div>
              <p className="mt-4 text-ocean-700">Loading ocean data...</p>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          {!loading && !error && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Data Sources Card */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-2xl font-semibold text-ocean-900 mb-4">
                  Data Sources
                </h2>
                {sources.length === 0 ? (
                  <p className="text-gray-600">No data sources configured yet.</p>
                ) : (
                  <ul className="space-y-3">
                    {sources.map((source) => (
                      <li
                        key={source.id}
                        className="flex items-center justify-between p-3 bg-ocean-50 rounded-md"
                      >
                        <div>
                          <p className="font-medium text-ocean-900">{source.name}</p>
                          <p className="text-sm text-gray-600">{source.description}</p>
                        </div>
                        <span
                          className={`px-2 py-1 text-xs rounded-full ${
                            source.is_active
                              ? 'bg-green-100 text-green-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          {source.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              {/* Locations Card */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-2xl font-semibold text-ocean-900 mb-4">
                  Monitoring Locations
                </h2>
                {locations.length === 0 ? (
                  <p className="text-gray-600">No monitoring locations available yet.</p>
                ) : (
                  <ul className="space-y-3">
                    {locations.slice(0, 5).map((location) => (
                      <li
                        key={location.id}
                        className="p-3 bg-ocean-50 rounded-md"
                      >
                        <p className="font-medium text-ocean-900">{location.name}</p>
                        <p className="text-sm text-gray-600">
                          {location.latitude.toFixed(4)}°, {location.longitude.toFixed(4)}°
                        </p>
                        {location.region && (
                          <p className="text-xs text-gray-500 mt-1">{location.region}</p>
                        )}
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              {/* Temperature Chart Card */}
              <div className="bg-white rounded-lg shadow-md p-6 md:col-span-2">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-4">
                  <h2 className="text-2xl font-semibold text-ocean-900">
                    Temperature Data
                  </h2>

                  {/* Location Selector */}
                  {locations.length > 0 && (
                    <div className="mt-4 md:mt-0 flex items-center gap-2">
                      <label className="text-sm text-gray-600">Location:</label>
                      <select
                        value={selectedLocation || ''}
                        onChange={(e) => setSelectedLocation(Number(e.target.value))}
                        className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-ocean-500"
                      >
                        {locations.map((loc) => (
                          <option key={loc.id} value={loc.id}>
                            {loc.name} ({loc.latitude.toFixed(2)}°, {loc.longitude.toFixed(2)}°)
                          </option>
                        ))}
                      </select>
                    </div>
                  )}
                </div>

                {hasTemperatureData ? (
                  <>
                    <TemperatureChart
                      locationId={selectedLocation}
                      startDate={startDate}
                      endDate={endDate}
                    />
                    {/* Date Range Info */}
                    <p className="text-sm text-gray-500 mt-4 text-center">
                      Showing data from {startDate} to {endDate}
                    </p>
                  </>
                ) : (
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-yellow-900 mb-2">
                      No Temperature Data Available
                    </h3>
                    <p className="text-yellow-800 mb-4">
                      To start seeing temperature data, run the NOAA data ingestion:
                    </p>
                    <ol className="list-decimal list-inside space-y-2 text-yellow-800">
                      <li>Run: <code className="bg-yellow-100 px-2 py-1 rounded">docker-compose exec backend python manage.py fetch_noaa_data</code></li>
                      <li>Wait for data to populate (~1-2 minutes)</li>
                      <li>Refresh this page</li>
                    </ol>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </main>
    </>
  );
}
