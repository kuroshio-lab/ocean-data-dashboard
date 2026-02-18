# frontend/CLAUDE.md

Guidance for Next.js frontend development. **Real-time + offline-first + simple for everyone.**

## Architecture Overview

```
Browser (Next.js + Recharts)
    ↓
Service Worker (offline cache, sync)
    ↓
Rate-limited API (polling every 30-60s)
    ↓
Django Backend (cached, aggregated responses)
```

### Key Stack
- **Framework**: Next.js 14+ with TypeScript
- **Charts**: Recharts (optimized for time-series data)
- **Styling**: Tailwind CSS
- **State**: React hooks (Context API for simple global state)
- **Caching**: Service Worker (offline + cache-first strategy)
- **Deployment**: Docker container (part of docker-compose)

## Design Philosophy

1. **Simple by default**: Non-technical users see clean, easy-to-understand dashboards
2. **Powerful when needed**: Advanced filtering + exports for marine scientists
3. **Offline-first**: Service Worker caches latest data. App works offline.
4. **Real-time feel**: Poll API every 30-60s for fresh observations
5. **Cost-conscious**: Leverage backend caching. Minimize API calls.

## Data Polling Strategy

Frontend polls backend for fresh data at regular intervals:

```typescript
// src/lib/api.ts
const POLLING_INTERVALS = {
  latest: 30_000,      // Latest values every 30 seconds (real-time feel)
  aggregated: 120_000, // Daily aggregations every 2 minutes (less critical)
  locations: 3600_000, // Location list every 1 hour (very stable)
};

// src/hooks/usePolling.ts
export const useLatestObservations = (locationId?: number) => {
  const [data, setData] = useState<Observation[]>([]);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const observations = await api.getLatestObservations({
          location_id: locationId
        });
        setData(observations);
      } catch (err) {
        setError(err as Error);
      }
    };

    fetchData(); // Fetch immediately
    const interval = setInterval(fetchData, POLLING_INTERVALS.latest);

    return () => clearInterval(interval);
  }, [locationId]);

  return { data, error, isLoading: !data && !error };
};
```

## Service Worker: Offline + Caching

Service Worker handles offline scenarios and respects backend cache TTLs:

```typescript
// public/sw.js
const CACHE_VERSION = 'v1';
const CACHE_STRATEGY = {
  '/api/locations/': { ttl: 3600 },        // 1 hour
  '/api/observations/latest/': { ttl: 300 }, // 5 minutes
  '/api/observations/aggregated/': { ttl: 21600 }, // 6 hours
};

self.addEventListener('fetch', (event) => {
  if (!event.request.url.includes('/api/')) {
    // Static assets: cache-first
    event.respondWith(cacheFirst(event.request));
    return;
  }

  // API calls: network-first, fallback to cache
  event.respondWith(networkFirstWithCache(event.request));
});

async function networkFirstWithCache(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_VERSION);
      cache.put(request, response.clone());
    }
    return response;
  } catch (err) {
    // Network failed, use cache
    return caches.match(request) || createOfflineResponse();
  }
}
```

Register in `src/pages/_app.tsx`:
```typescript
useEffect(() => {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js');
  }
}, []);
```

## Component Structure

### Simple Views (Default - General Public)

Components for non-technical users:

```
src/components/
├── Dashboard/
│   ├── LatestValueCard.tsx      # Big number + last update time
│   ├── TrendChart.tsx           # Simple line chart, last 7 days
│   └── LocationSelector.tsx     # Dropdown to pick location
├── Status/
│   ├── DataFreshness.tsx        # "Last updated 2 minutes ago"
│   └── ErrorBoundary.tsx        # Graceful error handling
└── Layout/
    ├── Header.tsx
    └── Footer.tsx
```

Example `LatestValueCard.tsx`:
```typescript
interface Props {
  location: Location;
  observationType: 'temperature' | 'salinity' | 'current' | 'chlorophyll';
}

export const LatestValueCard: React.FC<Props> = ({ location, observationType }) => {
  const { data, error } = useLatestObservations(location.id);
  const latest = data[observationType];

  if (error) return <div className="error">Data unavailable</div>;
  if (!latest) return <div className="skeleton">Loading...</div>;

  return (
    <div className="card">
      <h3>{observationType}</h3>
      <div className="value">{latest.value} {getUnit(observationType)}</div>
      <div className="metadata">
        Location: {location.name} | Updated: {formatTime(latest.timestamp)}
      </div>
      {latest.quality_flag !== 'good' && (
        <div className="warning">Quality: {latest.quality_flag}</div>
      )}
    </div>
  );
};
```

### Advanced Views (For Scientists)

Additional filtering + data export:

```
src/components/
└── Advanced/
    ├── AggregatedChart.tsx      # Min/max/avg over date range
    ├── MultiLocationCompare.tsx # Compare multiple locations
    ├── DataExport.tsx           # CSV/JSON download
    └── FilterPanel.tsx          # Date range, location, quality filters
```

Example `AggregatedChart.tsx`:
```typescript
interface Props {
  locationId: number;
  startDate: Date;
  endDate: Date;
  observationType: string;
}

export const AggregatedChart: React.FC<Props> = ({
  locationId,
  startDate,
  endDate,
  observationType,
}) => {
  const { data, error } = useAggregatedObservations({
    location_id: locationId,
    start_date: formatISO(startDate),
    end_date: formatISO(endDate),
    observation_type: observationType,
  });

  if (error) return <div className="error">{error.message}</div>;
  if (!data) return <div className="skeleton">Loading aggregations...</div>;

  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="min" stroke="#8884d8" />
        <Line type="monotone" dataKey="avg" stroke="#82ca9d" />
        <Line type="monotone" dataKey="max" stroke="#ffc658" />
      </LineChart>
    </ResponsiveContainer>
  );
};
```

## API Integration (Polling + Error Handling)

```typescript
// src/lib/api.ts
import axios from 'axios';

const client = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
  timeout: 10000,
});

// Intercept 429 (rate limited) and backoff
client.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 429) {
      const retryAfter = parseInt(
        error.response.headers['retry-after'] || '60'
      );
      console.warn(`Rate limited. Retrying in ${retryAfter}s`);
      // Exponential backoff + jitter
      await new Promise((r) => setTimeout(r, retryAfter * 1000));
      return client.request(error.config);
    }
    return Promise.reject(error);
  }
);

export const api = {
  getLatestObservations: async (params?: { location_id?: number }) => {
    const { data } = await client.get('/observations/latest/', { params });
    return data;
  },

  getAggregatedObservations: async (params: {
    location_id: number;
    start_date: string;
    end_date: string;
    observation_type: string;
  }) => {
    const { data } = await client.get('/observations/aggregated/', { params });
    return data;
  },

  getLocations: async () => {
    const { data } = await client.get('/locations/');
    return data;
  },
};
```

## TypeScript Types

```typescript
// src/types/index.ts
export interface Location {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  depth: number;
}

export interface Observation {
  location_id: number;
  timestamp: string; // ISO 8601
  value: number;
  quality_flag: 'good' | 'questionable' | 'bad';
  source: 'NOAA' | 'Copernicus' | 'NASA';
}

export interface AggregatedObservation {
  date: string; // ISO 8601 date
  location_id: number;
  min: number;
  max: number;
  avg: number;
  count: number;
}
```

## Performance Optimization

### Recharts Best Practices
```typescript
// ✅ GOOD: Memoized, limits data points
const TrendChart = React.memo(({ data }: Props) => {
  // Recharts struggles with 1000+ points. Downsample if needed.
  const downsampled = data.length > 500
    ? downsampleData(data, 500)
    : data;

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={downsampled}>
        {/* ... */}
      </LineChart>
    </ResponsiveContainer>
  );
});

// ✅ GOOD: Lazy load components
const AdvancedView = dynamic(() => import('./Advanced'), {
  loading: () => <div>Loading advanced features...</div>,
});
```

### Data Fetching Best Practices
```typescript
// ❌ BAD: Refetch every render
useEffect(() => {
  api.getLatestObservations();
}, []);

// ✅ GOOD: Cache results + only fetch on dependency change
const { data, isLoading } = useQuery(
  ['latest', locationId],
  () => api.getLatestObservations({ location_id: locationId }),
  { staleTime: 30_000 } // Don't refetch for 30s
);

// ✅ GOOD: Debounce filter changes
const [filters, setFilters] = useState({});
const debouncedFilters = useDebounce(filters, 500); // Wait 500ms after user stops typing
useEffect(() => {
  fetchData(debouncedFilters);
}, [debouncedFilters]);
```

## Error Handling & Resilience

```typescript
// src/components/ErrorBoundary.tsx
export const ErrorBoundary: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    const handler = (event: ErrorEvent) => {
      console.error('Uncaught error:', event.error);
      setHasError(true);
    };

    window.addEventListener('error', handler);
    return () => window.removeEventListener('error', handler);
  }, []);

  if (hasError) {
    return (
      <div className="error-page">
        <h1>Something went wrong</h1>
        <p>The app is having trouble. Please refresh the page.</p>
        <button onClick={() => window.location.reload()}>Refresh</button>
      </div>
    );
  }

  return <>{children}</>;
};
```

### API Error Responses
```typescript
// Handle rate limiting gracefully
if (error.status === 429) {
  return <div className="warning">Too many requests. Please wait a moment.</div>;
}

// Handle server errors
if (error.status >= 500) {
  return <div className="error">Data unavailable. Our team is investigating.</div>;
}

// Handle offline
if (!navigator.onLine) {
  return <div className="info">You're offline. Showing cached data.</div>;
}
```

## Testing

```bash
# Run tests in container
docker-compose exec frontend npm test

# Type check
docker-compose exec frontend npm run type-check

# Lint
docker-compose exec frontend npm run lint
```

Focus on:
- Data fetching with mocked API responses
- Component rendering with different data states (loading, error, empty)
- Polling intervals don't spam the API
- Service Worker caching behavior

## Deployment (Docker)

Frontend runs as a Next.js container in docker-compose:

```dockerfile
# Dockerfile (frontend)
FROM node:20-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
RUN npm install -g next@14
EXPOSE 3000
CMD ["node", "server.js"]
```

Environment variables (`frontend/.env.local`):
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api  # Local dev
NEXT_PUBLIC_APP_NAME=Ocean Data Dashboard
```

For production (AWS/GCP/Azure):
```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api
```

## Common Tasks

### Adding a New Chart Type
1. Create component in `src/components/`
2. Use `useLatestObservations()` or `useAggregatedObservations()` hook
3. Use Recharts with memoization for performance
4. Add to appropriate view (simple or advanced)

### Connecting to a New API Endpoint
1. Add method to `src/lib/api.ts`
2. Create TypeScript types in `src/types/index.ts`
3. Create custom hook in `src/hooks/` if reusable
4. Use in component with error boundaries

### Improving Mobile Experience
- Test on mobile devices / browser DevTools
- Use responsive grid (Tailwind's `grid-cols-1 md:grid-cols-2 lg:grid-cols-3`)
- Touch-friendly tap targets (min 48x48px)
- Service Worker enables offline for mobile users

## Important Notes

### Real-time is Polling, Not WebSockets
Polling every 30-60s gives the **feel** of real-time without backend complexity. Backend aggregations are already fresh (updated every 6 hours), so this is appropriate.

### Service Worker Cache Strategy
- Static assets: Cache-first (JS, CSS, images)
- API calls: Network-first, fallback to cache
- TTLs respect backend cache expiration

### Rate Limiting Handling
If you hit 429 (Too Many Requests):
- Backoff exponentially (wait 60s, then retry)
- Inform user: "Data is refreshing. Please wait."
- Don't spam retries

### Accessibility
- Use semantic HTML (`<button>`, `<nav>`, etc.)
- ARIA labels for charts (users with screen readers)
- Keyboard navigation (Tab through filters)
- Color contrast (WCAG AA minimum)

---

**See infra/CLAUDE.md** for Docker setup and deployment.
