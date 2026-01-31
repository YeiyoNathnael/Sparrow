import { useState, useEffect } from "react";
import { 
  Navigation, 
  Clock, 
  MapPin, 
  Bus,
  Phone,
  Zap
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { MapContainer, TileLayer, Marker, Popup, Polyline } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Fix leaflet default icon
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

L.Icon.Default.mergeOptions({
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

const API_URL = "http://localhost:8000/api";
const DUBAI_CENTER: [number, number] = [25.2048, 55.2708];

// Custom marker icons
const createCustomIcon = (color: string) => L.divIcon({
  className: 'custom-marker',
  html: `<div style="
    background: ${color};
    width: 32px;
    height: 32px;
    border-radius: 50% 50% 50% 0;
    transform: rotate(-45deg);
    border: 3px solid white;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
  "><div style="
    transform: rotate(45deg);
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: white;
    font-size: 14px;
  ">🚌</div></div>`,
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32],
});

const busIcon = createCustomIcon('#d22030');

export default function LiveMap() {
  const [routes, setRoutes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [peakHours, setPeakHours] = useState(true);
  const [selectedRoute, setSelectedRoute] = useState<any>(null);

  useEffect(() => {
    const fetchOptimizedRoutes = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${API_URL}/routes?peak_hours=${peakHours}`);
        if (!response.ok) throw new Error("Failed to fetch routes");
        const data = await response.json();
        
        if (data.routes && data.routes.length > 0) {
          setRoutes(data.routes);
        } else {
          // Fallback to demo routes if no data returned
          setRoutes(getDemoRoutes());
        }
      } catch (error) {
        console.error("Failed to fetch optimized routes:", error);
        // Use demo data on error
        setRoutes(getDemoRoutes());
      } finally {
        setLoading(false);
      }
    };

    fetchOptimizedRoutes();
  }, [peakHours]);

  const getDemoRoutes = () => {
    return [
      {
        id: "route_demo_1",
        route_number: 1,
        school_name: "Kings' School Al Barsha",
        student_count: 48,
        distance_km: 12.5,
        duration_minutes: 22.3,
        polyline: [
          [25.0934, 55.2341],
          [25.1000, 55.2350],
          [25.1100, 55.2400],
          [25.1200, 55.2450]
        ],
        optimization_score: 87.3,
        route_type: "peak_express",
        start_time: "06:30",
        status: "scheduled"
      },
      {
        id: "route_demo_2",
        route_number: 2,
        school_name: "Al Manara School",
        student_count: 42,
        distance_km: 10.8,
        duration_minutes: 19.5,
        polyline: [
          [25.1100, 55.2100],
          [25.1150, 55.2150],
          [25.1200, 55.2200],
          [25.1250, 55.2250]
        ],
        optimization_score: 92.1,
        route_type: "peak_express",
        start_time: "06:30",
        status: "scheduled"
      },
      {
        id: "route_demo_3",
        route_number: 3,
        school_name: "Dubai British School",
        student_count: 35,
        distance_km: 15.2,
        duration_minutes: 27.8,
        polyline: [
          [25.1200, 55.2500],
          [25.1300, 55.2550],
          [25.1400, 55.2600],
          [25.1500, 55.2700]
        ],
        optimization_score: 79.5,
        route_type: "standard",
        start_time: "07:30",
        status: "scheduled"
      }
    ];
  };

  const getRouteColor = (index: number) => {
    const colors = ["#d22030", "#00d4ff", "#10b981", "#fbbf24", "#a78bfa", "#f97316"];
    return colors[index % colors.length];
  };

  if (loading) {
    return (
      <div className="relative h-full w-full bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-foreground">Generating optimized routes with road snapping...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4 h-full flex flex-col">
      {/* Header with Peak Hours Toggle */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-foreground">Live Route Map</h2>
          <p className="text-sm text-muted-foreground">
            {routes.length} optimized routes with road-snapped navigation
          </p>
        </div>
        <div className="flex gap-2">
          <Button 
            variant={peakHours ? "default" : "outline"}
            onClick={() => setPeakHours(true)}
            size="sm"
            className="gap-2"
          >
            <Zap className="h-4 w-4" />
            Peak Hours (6:30 AM)
          </Button>
          <Button 
            variant={!peakHours ? "default" : "outline"}
            onClick={() => setPeakHours(false)}
            size="sm"
          >
            Off-Peak (7:30 AM)
          </Button>
        </div>
      </div>

      {/* Map Container */}
      <Card className="flex-1 overflow-hidden border">
        <div className="w-full h-full">
          <MapContainer 
            center={DUBAI_CENTER} 
            zoom={12} 
            style={{ width: '100%', height: '100%' }}
          >
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              maxZoom={19}
            />
          
          {/* Render all routes */}
          {routes.map((route, idx) => {
            const color = getRouteColor(idx);
            
            return (
              <div key={route.id}>
                {/* Road-snapped polyline */}
                {route.polyline && route.polyline.length > 1 && (
                  <Polyline
                    positions={route.polyline}
                    color={color}
                    weight={4}
                    opacity={0.8}
                    dashArray={route.route_type === "peak_express" ? "0" : "5, 5"}
                    className="cursor-pointer hover:opacity-100"
                    eventHandlers={{
                      click: () => setSelectedRoute(route)
                    }}
                  />
                )}
                
                {/* Bus start position marker */}
                {route.polyline && route.polyline.length > 0 && (
                  <Marker 
                    position={route.polyline[0]}
                    icon={busIcon}
                    eventHandlers={{
                      click: () => setSelectedRoute(route)
                    }}
                  >
                    <Popup className="text-xs">
                      <div>
                        <p className="font-bold">{route.school_name}</p>
                        <p>Route #{route.route_number}</p>
                        <p className="text-xs mt-1">
                          👥 {route.student_count} students | 
                          📏 {route.distance_km?.toFixed(1)} km
                        </p>
                      </div>
                    </Popup>
                  </Marker>
                )}
              </div>
            );
          })}
            </MapContainer>
        </div>
      </Card>

      {/* Routes List */}
      <div className="grid gap-2">
        <h3 className="font-semibold text-foreground flex items-center gap-2">
          <Bus className="h-4 w-4" />
          Route Overview
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 max-h-48 overflow-y-auto">
          {routes.slice(0, 12).map((route, idx) => (
            <Card 
              key={route.id}
              className={`cursor-pointer transition-all hover:border-primary ${selectedRoute?.id === route.id ? 'ring-2 ring-primary' : ''}`}
              onClick={() => setSelectedRoute(route)}
            >
              <CardContent className="p-3 space-y-2">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-xs text-muted-foreground">Route</p>
                    <p className="font-bold text-sm">{route.school_name}</p>
                  </div>
                  <Badge variant={route.status === "scheduled" ? "default" : "secondary"} className="text-xs">
                    {route.status}
                  </Badge>
                </div>
                
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="flex items-center gap-1">
                    <span className="text-muted-foreground">👥</span>
                    <span>{route.student_count}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <span className="text-muted-foreground">📏</span>
                    <span>{route.distance_km?.toFixed(1)} km</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <span className="text-muted-foreground">⏱️</span>
                    <span>{route.duration_minutes?.toFixed(0)} min</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <span className="text-muted-foreground">⭐</span>
                    <span className="text-success">{route.optimization_score?.toFixed(0)}%</span>
                  </div>
                </div>

                <div className="flex gap-1 pt-1">
                  <Badge variant="outline" className="text-xs bg-primary/10">
                    {route.route_type === "peak_express" ? "Express" : "Standard"}
                  </Badge>
                  <Badge variant="outline" className="text-xs">
                    {route.start_time}
                  </Badge>
                </div>

                <Button 
                  size="sm" 
                  className="w-full mt-2 h-7 text-xs gap-1"
                  onClick={(e) => {
                    e.stopPropagation();
                  }}
                >
                  <Phone className="h-3 w-3" />
                  Contact Driver
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Route Details */}
      {selectedRoute && (
        <Card className="border-primary bg-primary/5">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm">{selectedRoute.school_name} - Route #{selectedRoute.route_number}</CardTitle>
              <Button size="sm" variant="ghost" onClick={() => setSelectedRoute(null)}>✕</Button>
            </div>
          </CardHeader>
          <CardContent className="text-xs space-y-2">
            <div className="grid grid-cols-3 gap-2">
              <div className="flex items-center gap-2">
                <MapPin className="h-4 w-4 text-primary" />
                <span className="text-muted-foreground">{selectedRoute.distance_km?.toFixed(2)} km</span>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-primary" />
                <span className="text-muted-foreground">~{selectedRoute.duration_minutes?.toFixed(0)} mins</span>
              </div>
              <div className="flex items-center gap-2">
                <Navigation className="h-4 w-4 text-primary" />
                <span className="text-muted-foreground">Optimization: {selectedRoute.optimization_score?.toFixed(0)}%</span>
              </div>
            </div>
            <p className="text-muted-foreground">
              <strong>Route Type:</strong> {selectedRoute.route_type === "peak_express" ? "Peak Express" : "Standard"}
              <strong className="ml-3">Departure:</strong> {selectedRoute.start_time}
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
