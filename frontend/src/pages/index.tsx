import Head from 'next/head';
import { useEffect, useState } from 'react';
import api from '@/lib/api';
import type { Location, DataSource } from '@/types';

export default function Home() {
  const [locations, setLocations] = useState<Location[]>([]);
  const [sources, setSources] = useState<DataSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [locationsData, sourcesData] = await Promise.all([
        api.getLocations(),
        api.getDataSources(),
      ]);
      setLocations(locationsData);
      setSources(sourcesData);
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

              {/* Quick Stats Card */}
              <div className="bg-white rounded-lg shadow-md p-6 md:col-span-2">
                <h2 className="text-2xl font-semibold text-ocean-900 mb-4">
                  Getting Started
                </h2>
                <div className="prose max-w-none text-gray-700">
                  <p className="mb-4">
                    Welcome to the Ocean Data Dashboard! This platform provides real-time
                    visualization of oceanographic data from leading scientific sources.
                  </p>
                  <h3 className="text-lg font-semibold text-ocean-800 mb-2">
                    To start seeing data:
                  </h3>
                  <ol className="list-decimal list-inside space-y-2 mb-4">
                    <li>Run data ingestion: <code className="bg-gray-100 px-2 py-1 rounded">python manage.py fetch_noaa_data</code></li>
                    <li>Wait for data to populate (~1-2 minutes)</li>
                    <li>Refresh this page to see visualizations</li>
                  </ol>
                  <p className="text-sm text-gray-600">
                    Check the backend logs for ingestion status. Once data is available,
                    interactive charts will appear here automatically.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </>
  );
}
