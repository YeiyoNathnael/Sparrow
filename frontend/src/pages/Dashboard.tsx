import { 
  MapPin, 
  Bus, 
  Leaf, 
  Users, 
  Activity, 
  Cpu, 
  AlertCircle,
  CheckCircle,
  Clock,
  TrendingUp,
  Zap
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useState, useEffect } from "react";
import { API_URL } from "@/config/api";

const metrics = [
  { 
    label: "Total Zones", 
    value: "24", 
    change: "+3 this week",
    trend: "up",
    icon: MapPin,
    color: "accent"
  },
  { 
    label: "Buses Optimized", 
    value: "156", 
    change: "98.2% fleet",
    trend: "up",
    icon: Bus,
    color: "primary"
  },
  { 
    label: "CO₂ Reduction", 
    value: "12.4t", 
    change: "+8.3% vs last month",
    trend: "up",
    icon: Leaf,
    color: "success"
  },
  { 
    label: "Avg Capacity", 
    value: "78%", 
    change: "Optimal range",
    trend: "stable",
    icon: Users,
    color: "info"
  },
];

const notifications = [
  { id: 1, zone: "Al Barsha Zone 3", message: "Route optimization complete", time: "2 mins ago", status: "success" },
  { id: 2, zone: "Dubai Marina", message: "New students registered", time: "15 mins ago", status: "info" },
  { id: 3, zone: "Jumeirah", message: "Capacity threshold reached", time: "1 hour ago", status: "warning" },
  { id: 4, zone: "Downtown", message: "Driver schedule updated", time: "2 hours ago", status: "success" },
];

export default function Dashboard() {
  const [metrics, setMetrics] = useState([
    { 
      label: "Total Zones", 
      value: "24", 
      change: "+3 this week",
      trend: "up",
      icon: MapPin,
      color: "accent"
    },
    { 
      label: "Buses Optimized", 
      value: "156", 
      change: "98.2% fleet",
      trend: "up",
      icon: Bus,
      color: "primary"
    },
    { 
      label: "CO₂ Reduction", 
      value: "12.4t", 
      change: "+8.3% vs last month",
      trend: "up",
      icon: Leaf,
      color: "success"
    },
    { 
      label: "Avg Capacity", 
      value: "78%", 
      change: "Optimal range",
      trend: "stable",
      icon: Users,
      color: "info"
    },
  ]);

  const [loading, setLoading] = useState(true);
  const [avgDistance, setAvgDistance] = useState("0");
  const [avgStudentsPerRoute, setAvgStudentsPerRoute] = useState(0);
  const [efficiencyScore, setEfficiencyScore] = useState("0");
  const [highCongestion, setHighCongestion] = useState(0);
  const [mediumCongestion, setMediumCongestion] = useState(0);
  const [lowCongestion, setLowCongestion] = useState(0);
  const [totalDistance, setTotalDistance] = useState(0);
  const [routesCount, setRoutesCount] = useState(0);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        // Fetch schools, students, and routes from API
        const [schoolsRes, studentsRes, routesRes] = await Promise.all([
          fetch(`${API_URL}/schools`),
          fetch(`${API_URL}/students`),
          fetch(`${API_URL}/routes`),
        ]);

        if (!schoolsRes.ok || !studentsRes.ok || !routesRes.ok) throw new Error("Failed to fetch data");

        const schools = await schoolsRes.json();
        const students = await studentsRes.json();
        const routesData = await routesRes.json();
        const routes = routesData.routes || [];

        // Calculate metrics from real data
        const uniqueZones = new Set(schools.map((s: any) => s.cluster_zone || "Unknown")).size;
        const totalStudents = students.length;
        
        // Calculate capacity based on assembly points (number of buses)
        const totalAssemblyPoints = routes.reduce((sum: number, route: any) => sum + (route.num_pickups || 0), 0);
        const busCapacity = 50;
        const avgStudentsPerAssembly = totalAssemblyPoints > 0 ? totalStudents / totalAssemblyPoints : 0;
        const avgCapacityPercent = totalAssemblyPoints > 0 ? Math.round((avgStudentsPerAssembly / busCapacity) * 100) : 0;
        const capacityStatus = avgCapacityPercent <= 100 ? "Optimal" : `Over by ${avgCapacityPercent - 100}%`;
        const capacityColor = avgCapacityPercent <= 100 ? "info" : "warning";
        const capacityTrend = avgCapacityPercent <= 100 ? "up" : "warning";

        // Calculate route efficiency metrics
        const totalDistance = routes.reduce((sum: number, route: any) => sum + (route.distance_km || 0), 0);
        const avgDistance = routes.length > 0 ? (totalDistance / routes.length).toFixed(1) : "0";
        const avgStudentsPerRoute = routes.length > 0 ? Math.round(totalStudents / routes.length) : 0;
        const efficiencyScore = avgStudentsPerRoute > 0 ? ((totalDistance / totalStudents) * 10).toFixed(2) : "0";

        // Calculate school congestion (count routes per school)
        const schoolRouteCount: { [key: string]: number } = {};
        routes.forEach((route: any) => {
          const numDropoffs = route.num_dropoffs || 0;
          // Assuming each route visits different schools, count them
          for (let i = 0; i < numDropoffs; i++) {
            const schoolKey = `school_${i}`;
            schoolRouteCount[schoolKey] = (schoolRouteCount[schoolKey] || 0) + 1;
          }
        });
        
        const routeCounts = Object.values(schoolRouteCount);
        const highCongestion = routeCounts.filter((count: number) => count >= 4).length;
        const mediumCongestion = routeCounts.filter((count: number) => count >= 2 && count < 4).length;
        const lowCongestion = routeCounts.filter((count: number) => count < 2).length;

        // Set efficiency metrics
        setAvgDistance(avgDistance);
        setAvgStudentsPerRoute(avgStudentsPerRoute);
        setEfficiencyScore(efficiencyScore);
        setHighCongestion(highCongestion);
        setMediumCongestion(mediumCongestion);
        setLowCongestion(lowCongestion);
        setTotalDistance(totalDistance);
        setRoutesCount(routes.length);

        setMetrics([
          { 
            label: "Total Zones", 
            value: String(uniqueZones), 
            change: "Active zones",
            trend: "up",
            icon: MapPin,
            color: "accent"
          },
          { 
            label: "Active Routes", 
            value: String(routes.length), 
            change: "Optimized routes",
            trend: "up",
            icon: Bus,
            color: "primary"
          },
          { 
            label: "Total Students", 
            value: String(totalStudents), 
            change: "Registered",
            trend: "up",
            icon: Users,
            color: "success"
          },
          { 
            label: "Avg Capacity", 
            value: `${avgCapacityPercent}%`, 
            change: capacityStatus,
            trend: capacityTrend,
            icon: Leaf,
            color: "info"
          },
        ]);
      } catch (error) {
        console.error("Failed to fetch dashboard data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Executive Dashboard</h1>
          <p className="text-muted-foreground text-sm mt-1">Real-time fleet optimization overview</p>
        </div>
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Clock className="h-4 w-4" />
          <span>Last updated: Just now</span>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((metric, index) => (
          <Card 
            key={metric.label} 
            className={`metric-card group ${metric.trend === 'warning' ? 'border-warning/50' : ''}`}
            style={{ animationDelay: `${index * 100}ms` }}
          >
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">{metric.label}</p>
                  <p className="text-3xl font-bold text-foreground mt-2">{metric.value}</p>
                  <div className="flex items-center gap-1 mt-2">
                    {metric.trend === "up" && <TrendingUp className="h-3 w-3 text-success" />}
                    {metric.trend === "warning" && <AlertCircle className="h-3 w-3 text-warning" />}
                    <span className={`text-xs ${metric.trend === 'warning' ? 'text-warning' : 'text-muted-foreground'}`}>
                      {metric.change}
                    </span>
                  </div>
                </div>
                <div className={`p-3 rounded-xl transition-colors ${
                  metric.color === 'warning' 
                    ? 'bg-warning/10 group-hover:bg-warning/20' 
                    : `bg-${metric.color}/10 group-hover:bg-${metric.color}/20`
                }`}>
                  <metric.icon className={`h-6 w-6 ${
                    metric.color === 'warning' ? 'text-warning' : `text-${metric.color}`
                  }`} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Operational Metrics Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Route Efficiency Panel */}
        <Card className="glass">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Zap className="h-5 w-5 text-accent" />
              Route Efficiency
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="glass-subtle rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <MapPin className="h-4 w-4 text-primary" />
                  <p className="text-xs text-muted-foreground">Avg Distance</p>
                </div>
                <p className="text-2xl font-bold text-foreground font-mono">{avgDistance} km</p>
                <p className="text-xs text-muted-foreground mt-1">Per route</p>
              </div>
              
              <div className="glass-subtle rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Users className="h-4 w-4 text-success" />
                  <p className="text-xs text-muted-foreground">Avg Students</p>
                </div>
                <p className="text-2xl font-bold text-foreground font-mono">{avgStudentsPerRoute}</p>
                <p className="text-xs text-muted-foreground mt-1">Per route</p>
              </div>
            </div>
            
            <div className="glass-subtle rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Activity className="h-4 w-4 text-accent" />
                  <p className="text-xs text-muted-foreground">Efficiency Score</p>
                </div>
                <span className="text-xl font-bold text-accent font-mono">{efficiencyScore}</span>
              </div>
              <p className="text-xs text-muted-foreground">km per student × 10 (lower is better)</p>
            </div>
          </CardContent>
        </Card>

        {/* School Congestion Panel */}
        <Card className="glass">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center gap-2 text-lg">
              <AlertCircle className="h-5 w-5 text-warning" />
              School Congestion
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="glass-subtle rounded-lg p-4">
              <p className="text-xs text-muted-foreground mb-3">Routes per school distribution</p>
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="flex items-center justify-center gap-1 mb-1">
                    <div className="w-2 h-2 rounded-full bg-error"></div>
                    <p className="text-xs text-muted-foreground">High</p>
                  </div>
                  <p className="text-2xl font-bold text-error font-mono">{highCongestion}</p>
                  <p className="text-[10px] text-muted-foreground">4+ routes</p>
                </div>
                
                <div className="text-center">
                  <div className="flex items-center justify-center gap-1 mb-1">
                    <div className="w-2 h-2 rounded-full bg-warning"></div>
                    <p className="text-xs text-muted-foreground">Medium</p>
                  </div>
                  <p className="text-2xl font-bold text-warning font-mono">{mediumCongestion}</p>
                  <p className="text-[10px] text-muted-foreground">2-3 routes</p>
                </div>
                
                <div className="text-center">
                  <div className="flex items-center justify-center gap-1 mb-1">
                    <div className="w-2 h-2 rounded-full bg-success"></div>
                    <p className="text-xs text-muted-foreground">Low</p>
                  </div>
                  <p className="text-2xl font-bold text-success font-mono">{lowCongestion}</p>
                  <p className="text-[10px] text-muted-foreground">1 route</p>
                </div>
              </div>
            </div>
            
            <div className="glass-subtle rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-muted-foreground">Total Distance</p>
                  <p className="text-xl font-bold text-foreground font-mono">{totalDistance.toFixed(1)} km</p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-muted-foreground">All Routes</p>
                  <p className="text-xl font-bold text-primary font-mono">{routesCount}</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
