import { useState } from "react";
import { 
  Navigation, 
  User, 
  Clock, 
  MapPin, 
  Bus,
  Phone,
  ChevronRight,
  Layers,
  ZoomIn,
  ZoomOut,
  Locate,
  Users
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Fix for default marker icons in Leaflet with webpack/vite
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
const stopIcon = L.divIcon({
  className: 'custom-stop',
  html: `<div style="
    background: #00d4ff;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    border: 3px solid white;
    box-shadow: 0 0 10px rgba(0,212,255,0.6);
  "></div>`,
  iconSize: [14, 14],
  iconAnchor: [7, 7],
});

// Dubai coordinates and routes
const DUBAI_CENTER: [number, number] = [25.2048, 55.2708];

const activeRoutes = [
  { 
    id: "101", 
    driver: "Ahmed Al-Hassan", 
    stops: 4, 
    eta: "45 mins", 
    status: "on-time", 
    students: 32,
    busPosition: [25.1123, 55.1855] as [number, number], // Al Barsha
    route: [
      [25.1123, 55.1855],
      [25.1250, 55.2020],
      [25.1380, 55.2150],
      [25.1520, 55.2280],
      [25.1850, 55.2600],
    ] as [number, number][],
    color: "#00d4ff"
  },
  { 
    id: "102", 
    driver: "Mohammed Rashid", 
    stops: 6, 
    eta: "52 mins", 
    status: "on-time", 
    students: 28,
    busPosition: [25.0762, 55.1339] as [number, number], // Dubai Marina
    route: [
      [25.0762, 55.1339],
      [25.0900, 55.1500],
      [25.1100, 55.1700],
      [25.1350, 55.2000],
      [25.1600, 55.2350],
      [25.1850, 55.2600],
    ] as [number, number][],
    color: "#10b981"
  },
  { 
    id: "103", 
    driver: "Fatima Al-Sayed", 
    stops: 5, 
    eta: "38 mins", 
    status: "delayed", 
    students: 35,
    busPosition: [25.2100, 55.2700] as [number, number], // Downtown
    route: [
      [25.2100, 55.2700],
      [25.2000, 55.2550],
      [25.1900, 55.2400],
      [25.1750, 55.2300],
      [25.1850, 55.2600],
    ] as [number, number][],
    color: "#d22030"
  },
];

// Map controls component
function MapControls() {
  const map = useMap();
  
  return (
    <div className="absolute top-4 left-4 z-[1000] flex flex-col gap-2">
      <Button 
        size="icon" 
        variant="secondary" 
        className="glass h-10 w-10"
        onClick={() => map.zoomIn()}
      >
        <ZoomIn className="h-4 w-4" />
      </Button>
      <Button 
        size="icon" 
        variant="secondary" 
        className="glass h-10 w-10"
        onClick={() => map.zoomOut()}
      >
        <ZoomOut className="h-4 w-4" />
      </Button>
      <Button 
        size="icon" 
        variant="secondary" 
        className="glass h-10 w-10"
        onClick={() => map.setView(DUBAI_CENTER, 12)}
      >
        <Locate className="h-4 w-4" />
      </Button>
      <Button 
        size="icon" 
        variant="secondary" 
        className="glass h-10 w-10"
      >
        <Layers className="h-4 w-4" />
      </Button>
    </div>
  );
}

export default function LiveMap() {
  const [selectedRoute, setSelectedRoute] = useState<string | null>(null);

  return (
    <div className="relative h-[calc(100vh-8rem)] animate-fade-in rounded-xl overflow-hidden">
      {/* Leaflet Map */}
      <MapContainer
        center={DUBAI_CENTER}
        zoom={12}
        className="h-full w-full"
        zoomControl={false}
        style={{ background: '#0a0f1a' }}
      >
        {/* Dark map tiles */}
        <TileLayer
          attribution='&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>'
          url="https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png"
        />

        <MapControls />

        {/* Route polylines */}
        {activeRoutes.map((route) => (
          <Polyline
            key={route.id}
            positions={route.route}
            pathOptions={{
              color: route.color,
              weight: 4,
              opacity: selectedRoute === route.id ? 1 : 0.6,
              dashArray: route.status === 'delayed' ? '10, 10' : undefined,
            }}
            eventHandlers={{
              click: () => setSelectedRoute(route.id),
            }}
          />
        ))}

        {/* Bus stops */}
        {activeRoutes.map((route) => 
          route.route.slice(1).map((stop, idx) => (
            <Marker 
              key={`${route.id}-stop-${idx}`} 
              position={stop}
              icon={stopIcon}
            >
              <Popup className="custom-popup">
                <div className="text-sm">
                  <p className="font-semibold">Stop {idx + 1}</p>
                  <p className="text-muted-foreground">Route #{route.id}</p>
                </div>
              </Popup>
            </Marker>
          ))
        )}

        {/* Bus markers */}
        {activeRoutes.map((route) => (
          <Marker 
            key={route.id} 
            position={route.busPosition}
            icon={busIcon}
            eventHandlers={{
              click: () => setSelectedRoute(route.id),
            }}
          >
            <Popup>
              <div className="text-sm p-1">
                <p className="font-bold text-base">Route #{route.id}</p>
                <p className="text-muted-foreground">{route.driver}</p>
                <p className="mt-1">{route.students} students • {route.stops} stops</p>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 z-[1000] glass rounded-lg p-4">
        <p className="text-xs font-medium text-foreground mb-3">Active Routes</p>
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <div className="h-0.5 w-6 bg-accent rounded-full" />
            <span className="text-xs text-muted-foreground">On-time routes</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-0.5 w-6 bg-primary rounded-full" style={{ background: 'repeating-linear-gradient(90deg, #d22030, #d22030 4px, transparent 4px, transparent 8px)' }} />
            <span className="text-xs text-muted-foreground">Delayed routes</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-accent" style={{ boxShadow: '0 0 8px rgba(0,212,255,0.6)' }} />
            <span className="text-xs text-muted-foreground">Bus stops</span>
          </div>
        </div>
      </div>

      {/* Floating Route Detail Card */}
      <Card className="absolute top-4 right-4 w-80 z-[1000] glass animate-slide-in-right max-h-[calc(100%-2rem)] overflow-auto">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center justify-between text-base">
            <div className="flex items-center gap-2">
              <Navigation className="h-4 w-4 text-accent" />
              Active Routes
            </div>
            <span className="text-xs font-normal text-muted-foreground">{activeRoutes.length} active</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {activeRoutes.map((route) => (
            <div 
              key={route.id}
              className={`p-3 rounded-lg transition-colors cursor-pointer group ${
                selectedRoute === route.id 
                  ? 'bg-accent/10 border border-accent/30' 
                  : 'bg-secondary/50 hover:bg-secondary/70'
              }`}
              onClick={() => setSelectedRoute(route.id)}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 rounded-lg" style={{ background: `${route.color}20` }}>
                    <Bus className="h-4 w-4" style={{ color: route.color }} />
                  </div>
                  <span className="font-semibold text-foreground">Route #{route.id}</span>
                </div>
                <div className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${
                  route.status === 'on-time' 
                    ? 'bg-success/10 text-success border border-success/20' 
                    : 'bg-warning/10 text-warning border border-warning/20'
                }`}>
                  {route.status === 'on-time' ? 'On Time' : 'Delayed'}
                </div>
              </div>
              
              <div className="flex items-center gap-2 mb-2">
                <User className="h-3 w-3 text-muted-foreground" />
                <span className="text-sm text-foreground">{route.driver}</span>
              </div>

              <div className="grid grid-cols-3 gap-2 text-center pt-2 border-t border-border/50">
                <div>
                  <MapPin className="h-3 w-3 text-muted-foreground mx-auto mb-1" />
                  <p className="text-xs text-muted-foreground">Stops</p>
                  <p className="text-sm font-semibold text-foreground">{route.stops}</p>
                </div>
                <div>
                  <Clock className="h-3 w-3 text-muted-foreground mx-auto mb-1" />
                  <p className="text-xs text-muted-foreground">ETA</p>
                  <p className="text-sm font-semibold text-foreground">{route.eta}</p>
                </div>
                <div>
                  <Users className="h-3 w-3 text-muted-foreground mx-auto mb-1" />
                  <p className="text-xs text-muted-foreground">Students</p>
                  <p className="text-sm font-semibold text-foreground">{route.students}</p>
                </div>
              </div>

              <Button 
                variant="ghost" 
                size="sm" 
                className="w-full mt-3 text-accent hover:text-accent hover:bg-accent/10"
              >
                View Details
                <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <div className="absolute bottom-4 right-4 z-[1000] flex gap-2">
        <Button className="glass" variant="secondary">
          <Phone className="h-4 w-4 mr-2" />
          Contact Driver
        </Button>
        <Button className="bg-primary hover:bg-primary/90">
          <Navigation className="h-4 w-4 mr-2" />
          Track All
        </Button>
      </div>
    </div>
  );
}
