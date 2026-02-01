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
import { MapContainer, TileLayer, Marker, Popup, Polyline, CircleMarker } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import RoutingMachine from "@/components/map/RoutingMachine";

// Fix leaflet default icon
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

L.Icon.Default.mergeOptions({
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

const API_URL = "http://localhost:8000/api";
const AL_BARSHA_CENTER: [number, number] = [25.095, 55.22]; // Centered on Al Barsha area

// Create icon with emoji and number
const createStopIcon = (emoji: string, color: string, number?: number) => L.divIcon({
  className: 'custom-marker',
  html: `<div style="
    background: ${color};
    width: ${number !== undefined ? '28px' : '36px'};
    height: ${number !== undefined ? '28px' : '36px'};
    border-radius: 50% 50% 50% 0;
    transform: rotate(-45deg);
    border: 3px solid white;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    position: relative;
  "><div style="
    transform: rotate(45deg);
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: white;
    font-size: ${number !== undefined ? '10px' : '16px'};
    font-weight: bold;
  ">${number !== undefined ? number : emoji}</div></div>`,
  iconSize: [number !== undefined ? 28 : 36, number !== undefined ? 28 : 36],
  iconAnchor: [number !== undefined ? 14 : 18, number !== undefined ? 28 : 36],
  popupAnchor: [0, number !== undefined ? -28 : -36],
});

// Icon types
const createDepotIcon = (color: string) => createStopIcon('🚌', color);
const createPickupIcon = (number: number, color: string) => createStopIcon('', '#10b981', number); // Green for pickups
const createDropoffIcon = (number: number, color: string) => createStopIcon('', '#ef4444', number); // Red for dropoffs

export default function LiveMap() {
  const [routes, setRoutes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [peakHours, setPeakHours] = useState(true);
  const [selectedRoute, setSelectedRoute] = useState<any>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);

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
    const colors = ["#d22030", "#00d4ff", "#10b981", "#fbbf24", "#a78bfa", "#f97316", "#ec4899", "#14b8a6", "#8b5cf6", "#06b6d4"];
    return colors[index % colors.length];
  };

  // Check if a route is selected (for highlighting)
  const isRouteSelected = (route: any) => selectedRoute?.id === route.id;
  const hasSelection = selectedRoute !== null;

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
    <div className="relative h-screen w-full overflow-hidden">
      {/* Fullscreen Map */}
      <MapContainer 
        center={AL_BARSHA_CENTER} 
        zoom={13} 
        style={{ width: '100%', height: '100%' }}
        zoomControl={false}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          maxZoom={19}
        />
      
        {/* Render all routes */}
        {routes.map((route, idx) => {
          const color = getRouteColor(idx);
          const isSelected = isRouteSelected(route);
          const numPickups = route.num_pickups || 0;
          const numDropoffs = route.num_dropoffs || 0;
          
          // Hide unselected routes when a route is selected
          if (hasSelection && !isSelected) {
            return null;
          }
          
          return (
            <div key={route.id}>
              {/* Road-snapped route using OSRM - always enabled */}
              {route.polyline && route.polyline.length > 1 && (
                <RoutingMachine
                  waypoints={route.polyline}
                  color={color}
                  routeId={route.id}
                />
              )}
              
              {/* Depot (Bus Start) marker - first position */}
              {route.polyline && route.polyline.length > 0 && (
                <Marker 
                  position={route.polyline[0]}
                  icon={createDepotIcon(color)}
                  eventHandlers={{
                    click: () => setSelectedRoute(route)
                  }}
                >
                  <Popup className="text-xs">
                    <div>
                      <p className="font-bold text-lg">🚌 Bus #{route.route_number} Depot</p>
                      <p className="text-muted-foreground">Starting Point</p>
                      <p className="mt-2">
                        <strong>Students:</strong> {route.student_count}<br/>
                        <strong>Pickups:</strong> {numPickups} stops<br/>
                        <strong>Schools:</strong> {numDropoffs} stops<br/>
                        <strong>Distance:</strong> {route.distance_km?.toFixed(1)} km
                      </p>
                    </div>
                  </Popup>
                </Marker>
              )}
              
              {/* Pickup stops (Assembly Points) - green markers */}
              {route.polyline && route.polyline.slice(1, 1 + numPickups).map((pos: [number, number], i: number) => (
                <Marker
                  key={`pickup-${route.id}-${i}`}
                  position={pos}
                  icon={createPickupIcon(i + 1, color)}
                  eventHandlers={{
                    click: () => setSelectedRoute(route)
                  }}
                >
                  <Popup className="text-xs">
                    <div>
                      <p className="font-bold text-green-600">📍 Pickup #{i + 1}</p>
                      <p className="text-muted-foreground">Assembly Point</p>
                      <p className="mt-1 text-xs">
                        Route #{route.route_number}<br/>
                        Lat: {pos[0].toFixed(5)}<br/>
                        Lng: {pos[1].toFixed(5)}
                      </p>
                    </div>
                  </Popup>
                </Marker>
              ))}
              
              {/* Dropoff stops (Schools) - red markers */}
              {route.polyline && route.polyline.slice(1 + numPickups).map((pos: [number, number], i: number) => (
                <Marker
                  key={`dropoff-${route.id}-${i}`}
                  position={pos}
                  icon={createDropoffIcon(i + 1, color)}
                  eventHandlers={{
                    click: () => setSelectedRoute(route)
                  }}
                >
                  <Popup className="text-xs">
                    <div>
                      <p className="font-bold text-red-600">🏫 School #{i + 1}</p>
                      <p className="text-muted-foreground">
                        {route.school_names && route.school_names[i] ? route.school_names[i] : `Dropoff ${i + 1}`}
                      </p>
                      <p className="mt-1 text-xs">
                        Route #{route.route_number}<br/>
                        Lat: {pos[0].toFixed(5)}<br/>
                        Lng: {pos[1].toFixed(5)}
                      </p>
                    </div>
                  </Popup>
                </Marker>
              ))}
            </div>
          );
        })}
      </MapContainer>

      {/* Collapsible Sidebar - Left */}
      <div 
        className={`absolute top-0 left-0 h-full bg-background/95 backdrop-blur-sm border-r shadow-2xl transition-all duration-300 z-[1000] ${
          sidebarOpen ? 'w-80' : 'w-0'
        }`}
      >
        {sidebarOpen && (
          <div className="h-full flex flex-col p-4">
            {/* Sidebar Header */}
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-lg font-bold">Routes</h2>
                <p className="text-xs text-muted-foreground">{routes.length} active</p>
              </div>
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => setSidebarOpen(false)}
              >
                ✕
              </Button>
            </div>

            {/* Legend */}
            <div className="flex flex-col gap-1 mb-4 text-xs border-b pb-3">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-emerald-500"></span>
                <span>Pickup</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-red-500"></span>
                <span>School</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-amber-500"></span>
                <span>Depot</span>
              </div>
            </div>

            {/* Routes List - Scrollable */}
            <div className="flex-1 overflow-y-auto space-y-2">
              {routes.map((route, idx) => {
                const color = getRouteColor(idx);
                const isSelected = selectedRoute?.id === route.id;
                
                return (
                  <div
                    key={route.id}
                    className={`p-3 rounded-lg border-l-4 cursor-pointer transition-all ${
                      isSelected 
                        ? 'bg-primary/10 border-primary shadow-md' 
                        : 'bg-card hover:bg-accent border-transparent'
                    }`}
                    style={{ borderLeftColor: isSelected ? color : 'transparent' }}
                    onClick={() => setSelectedRoute(isSelected ? null : route)}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span 
                          className="w-3 h-3 rounded-full flex-shrink-0"
                          style={{ backgroundColor: color }}
                        ></span>
                        <span className="font-semibold text-sm">
                          Route #{route.route_number}
                        </span>
                        {route.buses_needed > 1 && (
                          <Badge variant="secondary" className="text-xs bg-amber-100 text-amber-800 border-amber-300">
                            🚌 ×{route.buses_needed}
                          </Badge>
                        )}
                      </div>
                      <Badge variant="outline" className="text-xs">
                        {route.id.replace('bus_', '#')}
                      </Badge>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div className="flex items-center gap-1">
                        <span>👥</span>
                        <span>{route.student_count}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <span>📏</span>
                        <span>{route.distance_km?.toFixed(1)} km</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <span className="text-emerald-500">📍</span>
                        <span>{route.num_pickups || 0} pickups</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <span className="text-red-500">🏫</span>
                        <span>{route.num_dropoffs || 0} schools</span>
                      </div>
                    </div>

                    {isSelected && (
                      <div className="mt-3 pt-3 border-t text-xs space-y-1">
                        <div className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          <span>{route.duration_minutes?.toFixed(0)} min</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Zap className="h-3 w-3" />
                          <span>{route.route_type === "peak_express" ? "Express" : "Standard"}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <span>⏰</span>
                          <span>{route.start_time}</span>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Sidebar Toggle Button - When Closed */}
      {!sidebarOpen && (
        <Button
          className="absolute top-4 left-4 z-[1000] shadow-lg"
          size="sm"
          onClick={() => setSidebarOpen(true)}
        >
          <Bus className="h-4 w-4 mr-2" />
          Routes ({routes.length})
        </Button>
      )}

      {/* Selected Route Details - Bottom */}
      {selectedRoute && (
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 z-[1000] w-11/12 max-w-3xl">
          <Card className="bg-background/95 backdrop-blur-sm shadow-2xl border-primary">
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span 
                    className="w-4 h-4 rounded-full"
                    style={{ backgroundColor: getRouteColor(routes.findIndex(r => r.id === selectedRoute.id)) }}
                  ></span>
                  <h3 className="font-bold">Bus {selectedRoute.id.replace('bus_', '#')} - Route #{selectedRoute.route_number}</h3>
                  {selectedRoute.buses_needed > 1 && (
                    <Badge variant="secondary" className="text-sm bg-amber-100 text-amber-800 border-amber-300">
                      🚌 ×{selectedRoute.buses_needed} buses needed
                    </Badge>
                  )}
                </div>
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => setSelectedRoute(null)}
                >
                  ✕
                </Button>
              </div>
              
              <div className="grid grid-cols-5 gap-4 text-sm">
                <div className="text-center">
                  <div className="text-2xl font-bold">{selectedRoute.student_count}</div>
                  <div className="text-xs text-muted-foreground">Students</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold">{selectedRoute.distance_km?.toFixed(1)}</div>
                  <div className="text-xs text-muted-foreground">km</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold">{selectedRoute.num_pickups || 0}</div>
                  <div className="text-xs text-muted-foreground">Pickups</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold">{selectedRoute.num_dropoffs || 0}</div>
                  <div className="text-xs text-muted-foreground">Schools</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold">{selectedRoute.duration_minutes?.toFixed(0)}</div>
                  <div className="text-xs text-muted-foreground">min</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
