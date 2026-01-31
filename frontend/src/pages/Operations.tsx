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
  Printer
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

const routeManifests = [
  { id: "101", zone: "Al Barsha", driver: "Ahmed Al-Hassan", students: 32, stops: 4, startTime: "06:30", status: "active" },
  { id: "102", zone: "Dubai Marina", driver: "Mohammed Rashid", students: 28, stops: 6, startTime: "06:45", status: "active" },
  { id: "103", zone: "Jumeirah", driver: "Fatima Al-Sayed", students: 35, stops: 5, startTime: "06:30", status: "delayed" },
  { id: "104", zone: "Downtown", driver: "Khalid Al-Mansoori", students: 30, stops: 4, startTime: "07:00", status: "pending" },
  { id: "105", zone: "Business Bay", driver: "Sara Ahmed", students: 26, stops: 5, startTime: "06:45", status: "active" },
  { id: "106", zone: "JBR", driver: "Omar Hassan", students: 33, stops: 6, startTime: "07:00", status: "completed" },
  { id: "107", zone: "Palm Jumeirah", driver: "Layla Mohammed", students: 24, stops: 3, startTime: "07:15", status: "pending" },
  { id: "108", zone: "DIFC", driver: "Yousef Ali", students: 29, stops: 4, startTime: "06:30", status: "active" },
];

const statusConfig = {
  active: { label: "Active", variant: "default" as const, className: "bg-success/10 text-success border-success/20" },
  pending: { label: "Pending", variant: "secondary" as const, className: "bg-warning/10 text-warning border-warning/20" },
  delayed: { label: "Delayed", variant: "destructive" as const, className: "bg-primary/10 text-primary border-primary/20" },
  completed: { label: "Completed", variant: "outline" as const, className: "bg-muted text-muted-foreground border-border" },
};

export default function Operations() {
  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Route Manifest</h1>
          <p className="text-muted-foreground text-sm mt-1">Manage driver sheets and daily operations</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="gap-2">
            <FileSpreadsheet className="h-4 w-4" />
            Export CSV
          </Button>
          <Button variant="outline" className="gap-2">
            <Printer className="h-4 w-4" />
            Print All
          </Button>
          <Button className="gap-2 bg-primary hover:bg-primary/90">
            <Download className="h-4 w-4" />
            Download PDF
          </Button>
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: "Total Routes", value: "24", icon: Bus, color: "accent" },
          { label: "Active Drivers", value: "18", icon: User, color: "success" },
          { label: "Students Today", value: "486", icon: Users, color: "primary" },
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
              <Button variant="outline" className="gap-2">
                <Filter className="h-4 w-4" />
                Filter
                <ChevronDown className="h-3 w-3" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="rounded-lg border border-border overflow-hidden">
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
                {routeManifests.map((route) => (
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
                        <Button variant="ghost" size="icon" className="h-8 w-8">
                          <Eye className="h-4 w-4 text-muted-foreground hover:text-foreground" />
                        </Button>
                        <Button variant="ghost" size="icon" className="h-8 w-8">
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
              Showing <span className="font-medium text-foreground">1-8</span> of <span className="font-medium text-foreground">24</span> routes
            </p>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" disabled>Previous</Button>
              <Button variant="outline" size="sm">Next</Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
