# Ocean Data Dashboard - Frontend

Next.js application for visualizing real-time oceanographic data.

## Features

- **Interactive Charts**: Recharts-powered data visualizations
- **Real-time Updates**: Live ocean data from backend API
- **Responsive Design**: Tailwind CSS for mobile-first UI
- **TypeScript**: Full type safety
- **SSR & SSG**: Next.js rendering strategies

## Tech Stack

- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Recharts
- Axios

## Setup

### Local Development

1. **Install dependencies**
```bash
npm install
```

2. **Configure environment**
```bash
cp .env.local.example .env.local
# Edit .env.local with your API URL
```

3. **Start development server**
```bash
npm run dev
```

4. **Open browser**
```
http://localhost:3000
```

### Docker Development

See main README.md for Docker setup instructions.

## Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run type-check   # Run TypeScript compiler
npm run format       # Format code with Prettier
```

## Project Structure

```
frontend/
├── src/
│   ├── components/        # React components
│   │   └── TemperatureChart.tsx
│   ├── pages/            # Next.js pages
│   │   ├── _app.tsx      # App wrapper
│   │   ├── _document.tsx # HTML document
│   │   └── index.tsx     # Home page
│   ├── lib/              # Utilities
│   │   ├── api.ts        # API client
│   │   └── utils.ts      # Helper functions
│   ├── types/            # TypeScript types
│   │   └── index.ts
│   └── styles/           # Global styles
│       └── globals.css
├── public/               # Static assets
├── next.config.js        # Next.js configuration
├── tailwind.config.ts    # Tailwind configuration
└── tsconfig.json         # TypeScript configuration
```

## API Integration

The frontend connects to the Django backend API. Configure the API URL in `.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### API Client

Located in `src/lib/api.ts`, provides methods for:
- Fetching data sources and locations
- Retrieving temperature, salinity, and current observations
- Getting time-series data for charts
- Accessing ingestion logs

Example usage:

```typescript
import api from '@/lib/api';

// Get all locations
const locations = await api.getLocations();

// Get temperature time series
const data = await api.getTemperatureTimeSeries({
  location: 1,
  start_date: '2024-01-01',
  end_date: '2024-01-31'
});
```

## Components

### TemperatureChart

Displays temperature data over time using Recharts.

```tsx
import TemperatureChart from '@/components/TemperatureChart';

<TemperatureChart
  locationId={1}
  startDate="2024-01-01"
  endDate="2024-01-31"
/>
```

## Styling

Uses Tailwind CSS with a custom ocean theme:

```typescript
// Colors available: ocean-50 through ocean-950
<div className="bg-ocean-100 text-ocean-900">
  Ocean themed content
</div>
```

Custom animations:
- `animate-wave`: Wave motion effect

## Type Safety

All API responses are fully typed. See `src/types/index.ts` for type definitions.

Example:

```typescript
import type { Location, TemperatureObservation } from '@/types';

const location: Location = {
  id: 1,
  name: 'California Coast',
  latitude: 36.9741,
  longitude: -122.0308,
  // ...
};
```

## Building for Production

```bash
# Build the application
npm run build

# Start production server
npm run start
```

The build creates optimized static files and server-side rendering.

## Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Import project in Vercel
3. Add environment variables
4. Deploy

### Docker

See main README.md for Docker deployment.

### AWS Amplify

1. Connect GitHub repository
2. Configure build settings:
   - Build command: `npm run build`
   - Output directory: `.next`
3. Add environment variables
4. Deploy

## Environment Variables

### Required

- `NEXT_PUBLIC_API_URL`: Backend API URL (e.g., `https://api.yourdomain.com/api`)
- `NEXT_PUBLIC_APP_NAME`: Application name (e.g., "Ocean Data Dashboard")

### Optional

- `NEXT_PUBLIC_GA_ID`: Google Analytics ID

## Troubleshooting

### API connection errors
- Verify `NEXT_PUBLIC_API_URL` is correct
- Ensure backend is running and accessible
- Check browser console for CORS errors

### Charts not displaying
- Ensure data exists in backend
- Check browser console for errors
- Verify API responses in Network tab

### Build errors
- Run `npm run type-check` to find type errors
- Clear `.next` directory: `rm -rf .next`
- Reinstall dependencies: `rm -rf node_modules && npm install`

## Performance Optimization

- Images optimized with Next.js Image component
- Code splitting with dynamic imports
- Server-side rendering for initial page load
- Static generation for blog/documentation pages

## Accessibility

- Semantic HTML
- ARIA labels on interactive elements
- Keyboard navigation support
- High contrast color scheme

## Browser Support

- Chrome (last 2 versions)
- Firefox (last 2 versions)
- Safari (last 2 versions)
- Edge (last 2 versions)

## Contributing

1. Create a feature branch
2. Write clean, typed code
3. Follow existing code style
4. Test in multiple browsers
5. Submit a pull request

## License

MIT
