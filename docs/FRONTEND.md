# Frontend Documentation

## Overview

The frontend is a **React + TypeScript** application built with **Vite** that provides an interactive map interface for visualizing optimized school bus routes. It uses **Leaflet** for mapping with **OSRM** integration for road-snapped route visualization.

---

## Architecture

```
frontend/src/
├── components/
│   ├── map/
│   │   └── RoutingMachine.tsx    # Leaflet Routing Machine wrapper
│   └── ui/                        # shadcn/ui components
├── pages/
│   └── LiveMap.tsx               # Main map page with route visualization
├── types/
│   └── leaflet-routing-machine.d.ts  # TypeScript declarations
└── App.tsx                        # Application entry point
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | React 18 | UI component library |
| Language | TypeScript | Type-safe JavaScript |
| Build Tool | Vite | Fast development server & bundler |
| Mapping | Leaflet + react-leaflet | Interactive maps |
| Road Snapping | leaflet-routing-machine + OSRM | Routes follow actual roads |
| UI Components | shadcn/ui | Modern component library |
| Styling | Tailwind CSS | Utility-first CSS |

---

## LiveMap Component

### File: `src/pages/LiveMap.tsx`

The main component responsible for displaying bus routes on an interactive map.

### State Management

```typescript
const [routes, setRoutes] = useState<any[]>([]);        // All routes from API
const [loading, setLoading] = useState(true);            // Loading state
const [peakHours, setPeakHours] = useState(true);        // Peak/off-peak filter
const [selectedRoute, setSelectedRoute] = useState<any>(null);  // Currently selected route
const [useRoadSnapping, setUseRoadSnapping] = useState(true);   // Road snapping toggle
```

### Key Variables

```typescript
const hasSelection = selectedRoute !== null;  // Whether any route is selected
const isRouteSelected = (route) => selectedRoute?.id === route.id;  // Check if specific route selected
```

---

## Route Visualization

### Marker Types

The map displays three types of markers with distinct appearances:

| Marker Type | Color | Icon | Description |
|-------------|-------|------|-------------|
| **Depot** | Route Color | 🚌 | Bus starting point (index 0 of polyline) |
| **Pickup** | Green (#10b981) | Number | Assembly points where students board |
| **Dropoff** | Red (#ef4444) | Number | Schools where students are dropped off |

### Icon Creation Functions

```typescript
// Create numbered stop icons
const createStopIcon = (emoji: string, color: string, number?: number) => L.divIcon({...});

// Specific icon types
const createDepotIcon = (color: string) => createStopIcon('🚌', color);
const createPickupIcon = (number: number, color: string) => createStopIcon('', '#10b981', number);
const createDropoffIcon = (number: number, color: string) => createStopIcon('', '#ef4444', number);
```

### Route Color Palette

```typescript
const getRouteColor = (index: number) => {
  const colors = [
    "#d22030",  // Red
    "#00d4ff",  // Cyan
    "#10b981",  // Green
    "#fbbf24",  // Yellow
    "#a78bfa",  // Purple
    "#f97316",  // Orange
    "#ec4899",  // Pink
    "#14b8a6",  // Teal
    "#8b5cf6",  // Violet
    "#06b6d4"   // Sky
  ];
  return colors[index % colors.length];
};
```

---

## Route Selection Behavior

### When No Route is Selected

- **Map**: Shows all routes with their respective colors
- **Route List**: All route cards displayed at full opacity
- **Markers**: All depot, pickup, and dropoff markers visible

### When a Route is Selected

- **Map**: Only the selected route is visible (others hidden)
- **Route List**: 
  - Selected card: Full size with all details, highlighted border
  - Other cards: Minimized (compact view), 40% opacity
- **Markers**: Only selected route's markers shown
- **Details Panel**: Expanded view with route sequence visualization

### Selection Logic

```typescript
// In the map rendering loop
if (hasSelection && !isSelected) {
  return null;  // Hide unselected routes from map
}

// In the route list
if (hasSelection && !isSelected) {
  // Return compact card with minimal info
  return (
    <Card className="opacity-40 hover:opacity-70">
      <p>Route #{route.route_number}</p>
      <p>{route.student_count} students</p>
    </Card>
  );
}
```

### Click Behavior

| Action | Result |
|--------|--------|
| Click unselected route card | Select that route, hide others |
| Click selected route card | Deselect, show all routes |
| Click marker on map | Select that route |
| Click '✕' on details panel | Deselect, show all routes |

---

## Polyline Data Structure

The backend sends route data with a specific polyline structure:

```
polyline = [
  [lat, lng],   // Index 0: Depot (starting point)
  [lat, lng],   // Index 1: First pickup (assembly point)
  [lat, lng],   // Index 2: Second pickup
  ...           // More pickups up to num_pickups
  [lat, lng],   // First dropoff (school)
  [lat, lng],   // Second dropoff
  ...           // Remaining schools
]
```

### Parsing Stops from Polyline

```typescript
const numPickups = route.num_pickups || 0;
const numDropoffs = route.num_dropoffs || 0;

// Depot: index 0
const depot = route.polyline[0];

// Pickups: indices 1 to (1 + num_pickups)
const pickups = route.polyline.slice(1, 1 + numPickups);

// Dropoffs: remaining indices
const dropoffs = route.polyline.slice(1 + numPickups);
```

---

## Road Snapping (OSRM Integration)

### RoutingMachine Component

Located at: `src/components/map/RoutingMachine.tsx`

Uses **Open Source Routing Machine (OSRM)** public server to snap routes to actual roads.

```typescript
interface RoutingMachineProps {
  waypoints: [number, number][];  // Array of [lat, lng] coordinates
  color: string;                   // Route line color
  routeId: string;                 // Unique identifier
  onRouteFound?: (route: any) => void;  // Callback when route calculated
}
```

### How It Works

1. Takes waypoints (stop coordinates) as input
2. Sends request to OSRM server: `router.project-osrm.org`
3. OSRM returns the actual road path between waypoints
4. Renders the snapped route on the map

### Toggle Behavior

```typescript
{useRoadSnapping && route.polyline.length > 1 && (
  <RoutingMachine waypoints={route.polyline} color={color} />
)}

{!useRoadSnapping && route.polyline.length > 1 && (
  <Polyline positions={route.polyline} color={color} />
)}
```

| Mode | Description |
|------|-------------|
| **Road Snapping ON** | Routes follow actual streets (OSRM) |
| **Road Snapping OFF** | Direct lines between stops (Polyline) |

---

## UI Components

### Route Card (Full)

Displayed when route is selected or no selection exists:

```
┌─────────────────────────────────────┐
│ Route #1              [scheduled]   │
│ ● Bus #0                            │
├─────────────────────────────────────┤
│ 👥 97 students    📏 25.6 km        │
│ 📍 3 pickups      🏫 20 schools     │
├─────────────────────────────────────┤
│ [Express] [06:00] [61 min]          │
├─────────────────────────────────────┤
│ [📞 Contact Driver]                 │  ← Only shown when selected
└─────────────────────────────────────┘
```

### Route Card (Compact)

Displayed for unselected routes when another route is selected:

```
┌─────────────────────────────────────┐
│ Route #2                            │
│ 63 students                         │
└─────────────────────────────────────┘
```

### Route Details Panel

Expanded panel shown below the map when a route is selected:

```
┌─────────────────────────────────────────────────────────────────┐
│ ● Bus #0 - Route #1                                        [✕]  │
├─────────────────────────────────────────────────────────────────┤
│ 📍 25.64 km   ⏱️ ~61 mins   📍 3 pickups   🏫 20 schools        │
├─────────────────────────────────────────────────────────────────┤
│ Route Sequence:                                                  │
│ [🚌 Depot] [📍 P1] [📍 P2] [📍 P3] → [🏫 S1] [🏫 S2] ... [+15]  │
├─────────────────────────────────────────────────────────────────┤
│ [🚀 Peak Express] [Departs: 06:00] [👥 97 students] [⭐ 89%]    │
└─────────────────────────────────────────────────────────────────┘
```

---

## API Integration

### Fetching Routes

```typescript
useEffect(() => {
  const fetchOptimizedRoutes = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/routes?peak_hours=${peakHours}`);
      const data = await response.json();
      
      if (data.routes && data.routes.length > 0) {
        setRoutes(data.routes);
      } else {
        setRoutes(getDemoRoutes());  // Fallback demo data
      }
    } catch (error) {
      setRoutes(getDemoRoutes());  // Use demo on error
    } finally {
      setLoading(false);
    }
  };

  fetchOptimizedRoutes();
}, [peakHours]);  // Re-fetch when peak_hours changes
```

### API Configuration

```typescript
const API_URL = "http://localhost:8000/api";
const AL_BARSHA_CENTER: [number, number] = [25.0950, 55.2200];
```

---

## Map Configuration

### Initial View

```typescript
<MapContainer 
  center={AL_BARSHA_CENTER}  // [25.0950, 55.2200] - Al Barsha, Dubai
  zoom={14}                   // Street-level zoom
  style={{ width: '100%', height: '100%', minHeight: '400px' }}
>
```

### Tile Layer (OpenStreetMap)

```typescript
<TileLayer
  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
  attribution='&copy; OpenStreetMap contributors'
  maxZoom={19}
/>
```

---

## Legend

The UI includes a legend explaining marker colors:

```typescript
<div className="flex gap-2 mb-2 text-xs">
  <span className="flex items-center gap-1">
    <span className="w-3 h-3 rounded-full bg-emerald-500"></span>
    Pickup (Assembly Point)
  </span>
  <span className="flex items-center gap-1">
    <span className="w-3 h-3 rounded-full bg-red-500"></span>
    Dropoff (School)
  </span>
  <span className="flex items-center gap-1">
    <span className="w-3 h-3 rounded-full bg-amber-500"></span>
    🚌 Bus Depot
  </span>
</div>
```

---

## Running the Frontend

```bash
cd frontend
npm install
npm run dev
```

Development server runs at: `http://localhost:8080` (or 8081/8082 if port in use)

### Build for Production

```bash
npm run build
```

Output directory: `dist/`

---

## Component Hierarchy

```
App.tsx
└── LiveMap.tsx
    ├── MapContainer (Leaflet)
    │   ├── TileLayer (OpenStreetMap)
    │   └── {routes.map()}
    │       ├── RoutingMachine (if road snapping enabled)
    │       ├── Polyline (if road snapping disabled)
    │       ├── Marker (Depot)
    │       ├── Marker[] (Pickups)
    │       └── Marker[] (Dropoffs)
    ├── Route Cards Grid
    │   └── Card[] (route list)
    └── Route Details Panel (if selected)
```

---

## Performance Considerations

1. **Conditional Rendering**: Unselected routes return `null` to avoid rendering
2. **OSRM Caching**: leaflet-routing-machine caches route calculations
3. **Lazy Loading**: Only visible route markers are rendered
4. **Memoization**: Route color calculation is deterministic by index
