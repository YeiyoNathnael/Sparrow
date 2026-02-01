import { 
  FileText, 
  Download, 
  Search, 
  Filter, 
  Bus, 
  User, 
  MapPin, 
  Clock,
  Users,
  ChevronDown,
  Eye,
  FileSpreadsheet,
  Printer,
  AlertCircle
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { useState, useRef, useEffect } from "react";
import { exportToCSV, exportToJSON, printContent, RouteData } from "@/services/exportService";
import { FilterDialog } from "@/components/dialogs";
import { useRouteFilters } from "@/hooks/useAppState";
import { API_URL } from "@/config/api";

const statusConfig = {
  active: { label: "Active", variant: "default" as const, className: "bg-success/10 text-success border-success/20" },
  pending: { label: "Pending", variant: "secondary" as const, className: "bg-warning/10 text-warning border-warning/20" },
  delayed: { label: "Delayed", variant: "destructive" as const, className: "bg-primary/10 text-primary border-primary/20" },
  completed: { label: "Completed", variant: "outline" as const, className: "bg-muted text-muted-foreground border-border" },
};

export default function Operations() {
  const [routeManifests, setRouteManifests] = useState<any[]>([]);
  const [filteredRoutes, setFilteredRoutes] = useState<any[]>([]);
  const [selectedRoute, setSelectedRoute] = useState<any | null>(null);
  const [showDetails, setShowDetails] = useState(false);
  const [loading, setLoading] = useState(true);
  const tableRef = useRef<HTMLDivElement>(null);
  const { filters, isOpen, setIsOpen, updateFilter, clearFilters } = useRouteFilters();

  // Fetch routes from API
  useEffect(() => {
    const fetchRoutes = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${API_URL}/routes`);
        if (!response.ok) throw new Error("Failed to fetch routes");
        const data = await response.json();
        
        // Map API response to route manifests format
        const manifests = data.map((route: any) => ({
          id: route.id || String(Math.random()),
          zone: route.zone || "Unknown",
          driver: route.driver || "Unassigned",
          students: route.student_count || 0,
          stops: route.stops || 0,
          startTime: route.start_time || "06:30",
          status: route.status || "pending",
        }));
        
        setRouteManifests(manifests);
        setFilteredRoutes(manifests);
      } catch (error) {
        console.error("Failed to fetch routes:", error);
        // Fallback to default routes if API fails
        const defaults = [
          { id: "101", zone: "Al Barsha", driver: "Ahmed Al-Hassan", students: 32, stops: 4, startTime: "06:30", status: "active" },
          { id: "102", zone: "Dubai Marina", driver: "Mohammed Rashid", students: 28, stops: 6, startTime: "06:45", status: "active" },
          { id: "103", zone: "Jumeirah", driver: "Fatima Al-Sayed", students: 35, stops: 5, startTime: "06:30", status: "delayed" },
          { id: "104", zone: "Downtown", driver: "Khalid Al-Mansoori", students: 30, stops: 4, startTime: "07:00", status: "pending" },
        ];
        setRouteManifests(defaults);
        setFilteredRoutes(defaults);
      } finally {
        setLoading(false);
      }
    };

    fetchRoutes();
  }, []);

  const zones = Array.from(new Set(routeManifests.map(r => r.zone)));
  const drivers = Array.from(new Set(routeManifests.map(r => r.driver)));

  const handleExportCSV = () => {
    const data = filteredRoutes.map(r => ({
      id: r.id,
      zone: r.zone,
      driver: r.driver,
      students: r.students,
      stops: r.stops,
      startTime: r.startTime,
      status: r.status,
    }));
    exportToCSV(data);
  };

  const handleExportPDF = () => {
    if (tableRef.current) {
      printContent(tableRef.current, 'Route Manifests - RTA NEXUS');
    }
  };

  const handlePrintAll = () => {
    if (tableRef.current) {
      printContent(tableRef.current, 'All Route Manifests');
    }
  };

  const handleFilter = (filterOptions: any) => {
    let filtered = routeManifests;

    if (filterOptions.status) {
      filtered = filtered.filter(r => r.status === filterOptions.status);
    }
    if (filterOptions.zone) {
      filtered = filtered.filter(r => r.zone === filterOptions.zone);
    }
    if (filterOptions.driver) {
      filtered = filtered.filter(r => r.driver === filterOptions.driver);
    }

    setFilteredRoutes(filtered);
  };

  const handleViewDetails = (route: typeof routeManifests[0]) => {
    setSelectedRoute(route);
    setShowDetails(true);
  };

  const handleDownloadRoute = (route: typeof routeManifests[0]) => {
    const routeData = {
      ...route,
      coordinates: route.zone, // Bus pooling system would add actual coordinates
      timestamp: new Date().toISOString(),
    };
    exportToJSON(routeData);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Route Manifest</h1>
          <p className="text-muted-foreground text-sm mt-1">Manage driver sheets and daily operations</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="gap-2" onClick={handleExportCSV}>
            <FileSpreadsheet className="h-4 w-4" />
            Export CSV
          </Button>
          <Button variant="outline" className="gap-2" onClick={handlePrintAll}>
            <Printer className="h-4 w-4" />
            Print All
          </Button>
          <Button className="gap-2 bg-primary hover:bg-primary/90" onClick={handleExportPDF}>
            <Download className="h-4 w-4" />
            Download PDF
          </Button>
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: "Total Routes", value: filteredRoutes.length.toString(), icon: Bus, color: "accent" },
          { label: "Active Drivers", value: Array.from(new Set(filteredRoutes.map(r => r.driver))).length.toString(), icon: User, color: "success" },
          { label: "Students Today", value: filteredRoutes.reduce((a, b) => a + b.students, 0).toString(), icon: Users, color: "primary" },
          { label: "Avg. Route Time", value: "42 min", icon: Clock, color: "info" },
        ].map((stat) => (
          <Card key={stat.label} className="glass-subtle">
            <CardContent className="p-4 flex items-center gap-4">
              <div className={`p-3 rounded-xl bg-${stat.color}/10`}>
                <stat.icon className={`h-5 w-5 text-${stat.color}`} />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">{stat.label}</p>
                <p className="text-2xl font-bold text-foreground">{stat.value}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Table Card */}
      <Card className="glass">
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-accent" />
              Today's Manifests
            </CardTitle>
            <div className="flex gap-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input 
                  placeholder="Search routes..." 
                  className="pl-9 w-64 bg-secondary/50"
                />
              </div>
              <Button variant="outline" className="gap-2" onClick={() => setIsOpen(true)}>
                <Filter className="h-4 w-4" />
                Filter
                <ChevronDown className="h-3 w-3" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="rounded-lg border border-border overflow-hidden" ref={tableRef}>
            <Table>
              <TableHeader>
                <TableRow className="bg-secondary/50 hover:bg-secondary/50">
                  <TableHead className="font-semibold">Route ID</TableHead>
                  <TableHead className="font-semibold">Zone</TableHead>
                  <TableHead className="font-semibold">Driver</TableHead>
                  <TableHead className="font-semibold text-center">Students</TableHead>
                  <TableHead className="font-semibold text-center">Stops</TableHead>
                  <TableHead className="font-semibold">Start Time</TableHead>
                  <TableHead className="font-semibold">Status</TableHead>
                  <TableHead className="font-semibold text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredRoutes.map((route) => (
                  <TableRow key={route.id} className="hover:bg-secondary/30">
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Bus className="h-4 w-4 text-accent" />
                        <span className="font-mono font-medium">#{route.id}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <MapPin className="h-3 w-3 text-muted-foreground" />
                        {route.zone}
                      </div>
                    </TableCell>
                    <TableCell>{route.driver}</TableCell>
                    <TableCell className="text-center font-mono">{route.students}</TableCell>
                    <TableCell className="text-center font-mono">{route.stops}</TableCell>
                    <TableCell className="font-mono">{route.startTime}</TableCell>
                    <TableCell>
                      <Badge 
                        variant={statusConfig[route.status as keyof typeof statusConfig].variant}
                        className={statusConfig[route.status as keyof typeof statusConfig].className}
                      >
                        {statusConfig[route.status as keyof typeof statusConfig].label}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-1">
                        <Button 
                          variant="ghost" 
                          size="icon" 
                          className="h-8 w-8"
                          onClick={() => handleViewDetails(route)}
                        >
                          <Eye className="h-4 w-4 text-muted-foreground hover:text-foreground" />
                        </Button>
                        <Button 
                          variant="ghost" 
                          size="icon" 
                          className="h-8 w-8"
                          onClick={() => handleDownloadRoute(route)}
                        >
                          <Download className="h-4 w-4 text-muted-foreground hover:text-foreground" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between mt-4 pt-4 border-t border-border">
            <p className="text-sm text-muted-foreground">
              Showing <span className="font-medium text-foreground">1-{filteredRoutes.length}</span> of <span className="font-medium text-foreground">24</span> routes
            </p>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" disabled>Previous</Button>
              <Button variant="outline" size="sm">Next</Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Filter Dialog */}
      <FilterDialog
        isOpen={isOpen}
        onOpenChange={setIsOpen}
        onFilter={handleFilter}
        zones={zones}
        drivers={drivers}
      />

      {/* Route Details Modal */}
      <Dialog open={showDetails} onOpenChange={setShowDetails}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Route Details - #{selectedRoute?.id}</DialogTitle>
          </DialogHeader>
          
          {selectedRoute && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 rounded-lg bg-secondary/50">
                  <p className="text-xs text-muted-foreground">Driver</p>
                  <p className="text-foreground font-semibold mt-1">{selectedRoute.driver}</p>
                </div>
                <div className="p-4 rounded-lg bg-secondary/50">
                  <p className="text-xs text-muted-foreground">Zone</p>
                  <p className="text-foreground font-semibold mt-1">{selectedRoute.zone}</p>
                </div>
                <div className="p-4 rounded-lg bg-secondary/50">
                  <p className="text-xs text-muted-foreground">Students</p>
                  <p className="text-foreground font-semibold mt-1">{selectedRoute.students}</p>
                </div>
                <div className="p-4 rounded-lg bg-secondary/50">
                  <p className="text-xs text-muted-foreground">Stops</p>
                  <p className="text-foreground font-semibold mt-1">{selectedRoute.stops}</p>
                </div>
              </div>

              <div className="p-4 rounded-lg bg-primary/10 border border-primary/20 flex gap-3">
                <AlertCircle className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-foreground">Route Optimization Available</p>
                  <p className="text-sm text-muted-foreground mt-1">
                    This route can be optimized to reduce travel time by up to 15%. Visit the Optimization Studio to run the ML model.
                  </p>
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-4">
                <Button variant="outline" onClick={() => setShowDetails(false)}>Close</Button>
                <Button className="bg-accent hover:bg-accent/90">View on Map</Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
