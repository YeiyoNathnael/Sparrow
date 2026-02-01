import { useEffect } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet-routing-machine';
import 'leaflet-routing-machine/dist/leaflet-routing-machine.css';

interface RoutingMachineProps {
  waypoints: [number, number][];
  color: string;
  routeId: string;
  onRouteFound?: (distance: number, duration: number) => void;
}

/**
 * Component that renders a road-snapped route using Leaflet Routing Machine
 * with OSRM (Open Source Routing Machine) backend
 */
export default function RoutingMachine({ 
  waypoints, 
  color, 
  routeId,
  onRouteFound 
}: RoutingMachineProps) {
  const map = useMap();

  useEffect(() => {
    if (!map || waypoints.length < 2) return;

    // Create waypoints for routing
    const routeWaypoints = waypoints.map(([lat, lng]) => 
      L.latLng(lat, lng)
    );

    // Create routing control with OSRM
    const routingControl = L.Routing.control({
      waypoints: routeWaypoints,
      router: L.Routing.osrmv1({
        serviceUrl: 'https://router.project-osrm.org/route/v1',
        profile: 'driving'
      }),
      lineOptions: {
        styles: [
          { 
            color: color, 
            weight: 5, 
            opacity: 0.8 
          }
        ],
        extendToWaypoints: true,
        missingRouteTolerance: 0
      },
      // Hide the control panel - we just want the route line
      show: false,
      addWaypoints: false,
      routeWhileDragging: false,
      fitSelectedRoutes: false,
      showAlternatives: false,
      // Hide default markers - we'll use our own
      createMarker: () => null
    }).addTo(map);

    // Listen for route found event
    routingControl.on('routesfound', (e: any) => {
      const route = e.routes[0];
      if (onRouteFound && route) {
        onRouteFound(
          route.summary.totalDistance / 1000, // Convert to km
          route.summary.totalTime / 60 // Convert to minutes
        );
      }
    });

    // Handle routing errors gracefully
    routingControl.on('routingerror', (e: any) => {
      console.warn(`Routing error for route ${routeId}:`, e.error?.message);
    });

    // Cleanup on unmount
    return () => {
      if (map && routingControl) {
        map.removeControl(routingControl);
      }
    };
  }, [map, waypoints, color, routeId, onRouteFound]);

  return null;
}
