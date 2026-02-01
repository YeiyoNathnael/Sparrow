declare module 'leaflet-routing-machine' {
  import * as L from 'leaflet';

  namespace Routing {
    interface RoutingControlOptions {
      waypoints?: L.LatLng[];
      router?: any;
      plan?: any;
      geocoder?: any;
      fitSelectedRoutes?: boolean | string;
      lineOptions?: {
        styles?: {
          color?: string;
          weight?: number;
          opacity?: number;
          dashArray?: string;
        }[];
        extendToWaypoints?: boolean;
        missingRouteTolerance?: number;
      };
      routeLine?: (route: any, options: any) => L.Polyline;
      autoRoute?: boolean;
      routeWhileDragging?: boolean;
      routeDragInterval?: number;
      waypointMode?: string;
      useZoomParameter?: boolean;
      showAlternatives?: boolean;
      altLineOptions?: any;
      show?: boolean;
      addWaypoints?: boolean;
      createMarker?: (i: number, waypoint: any, n: number) => L.Marker | null;
    }

    interface RoutingControl extends L.Control {
      getWaypoints(): L.LatLng[];
      setWaypoints(waypoints: L.LatLng[]): this;
      spliceWaypoints(index: number, waypointsToRemove: number, ...waypoints: L.LatLng[]): L.LatLng[];
      getPlan(): any;
      getRouter(): any;
      route(): void;
      on(type: string, fn: (e: any) => void): this;
    }

    function control(options?: RoutingControlOptions): RoutingControl;
    function osrmv1(options?: { serviceUrl?: string; profile?: string }): any;
  }
}

declare module 'leaflet' {
  namespace Routing {
    interface RoutingControlOptions {
      waypoints?: L.LatLng[];
      router?: any;
      plan?: any;
      geocoder?: any;
      fitSelectedRoutes?: boolean | string;
      lineOptions?: {
        styles?: {
          color?: string;
          weight?: number;
          opacity?: number;
          dashArray?: string;
        }[];
        extendToWaypoints?: boolean;
        missingRouteTolerance?: number;
      };
      routeLine?: (route: any, options: any) => L.Polyline;
      autoRoute?: boolean;
      routeWhileDragging?: boolean;
      routeDragInterval?: number;
      waypointMode?: string;
      useZoomParameter?: boolean;
      showAlternatives?: boolean;
      altLineOptions?: any;
      show?: boolean;
      addWaypoints?: boolean;
      createMarker?: (i: number, waypoint: any, n: number) => L.Marker | null;
    }

    interface RoutingControl extends L.Control {
      getWaypoints(): L.LatLng[];
      setWaypoints(waypoints: L.LatLng[]): this;
      spliceWaypoints(index: number, waypointsToRemove: number, ...waypoints: L.LatLng[]): L.LatLng[];
      getPlan(): any;
      getRouter(): any;
      route(): void;
      on(type: string, fn: (e: any) => void): this;
    }

    function control(options?: RoutingControlOptions): RoutingControl;
    function osrmv1(options?: { serviceUrl?: string; profile?: string }): any;
  }
}
