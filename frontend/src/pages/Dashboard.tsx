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
            className="metric-card group"
            style={{ animationDelay: `${index * 100}ms` }}
          >
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">{metric.label}</p>
                  <p className="text-3xl font-bold text-foreground mt-2">{metric.value}</p>
                  <div className="flex items-center gap-1 mt-2">
                    {metric.trend === "up" && <TrendingUp className="h-3 w-3 text-success" />}
                    <span className="text-xs text-muted-foreground">{metric.change}</span>
                  </div>
                </div>
                <div className={`p-3 rounded-xl bg-${metric.color}/10 group-hover:bg-${metric.color}/20 transition-colors`}>
                  <metric.icon className={`h-6 w-6 text-${metric.color}`} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* System Health & Notifications Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* System Health Panel */}
        <Card className="glass lg:col-span-2">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Activity className="h-5 w-5 text-accent" />
              System Health
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* PyTorch Model Status */}
            <div className="glass-subtle rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-success/10">
                    <Cpu className="h-5 w-5 text-success" />
                  </div>
                  <div>
                    <p className="font-medium text-foreground">PyTorch Model</p>
                    <p className="text-xs text-muted-foreground font-mono">K-Means Clustering v2.4</p>
                  </div>
                </div>
                <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-success/10 border border-success/20">
                  <CheckCircle className="h-3.5 w-3.5 text-success" />
                  <span className="text-xs font-medium text-success">Converged</span>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4 pt-3 border-t border-border/50">
                <div>
                  <p className="text-xs text-muted-foreground">Iterations</p>
                  <p className="text-lg font-semibold text-foreground font-mono">847</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Loss</p>
                  <p className="text-lg font-semibold text-success font-mono">0.0024</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Accuracy</p>
                  <p className="text-lg font-semibold text-foreground font-mono">99.2%</p>
                </div>
              </div>
            </div>

            {/* Cluster Quality */}
            <div className="glass-subtle rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-accent/10">
                    <Zap className="h-5 w-5 text-accent" />
                  </div>
                  <div>
                    <p className="font-medium text-foreground">Cluster Quality</p>
                    <p className="text-xs text-muted-foreground">Silhouette Score Analysis</p>
                  </div>
                </div>
                <span className="text-2xl font-bold text-accent font-mono">0.65</span>
              </div>
              <div className="w-full h-2 rounded-full bg-secondary overflow-hidden">
                <div 
                  className="h-full rounded-full bg-gradient-to-r from-accent to-accent/60 transition-all duration-1000"
                  style={{ width: "65%" }}
                />
              </div>
              <p className="text-xs text-muted-foreground mt-2">Above threshold (0.50) — Good clustering separation</p>
            </div>
          </CardContent>
        </Card>

        {/* Notification Feed */}
        <Card className="glass">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center gap-2 text-lg">
              <AlertCircle className="h-5 w-5 text-primary" />
              Activity Feed
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {notifications.map((notification) => (
                <div 
                  key={notification.id}
                  className="flex items-start gap-3 p-3 rounded-lg bg-secondary/30 hover:bg-secondary/50 transition-colors"
                >
                  <div className={`mt-0.5 h-2 w-2 rounded-full flex-shrink-0 ${
                    notification.status === 'success' ? 'bg-success' :
                    notification.status === 'warning' ? 'bg-warning' : 'bg-info'
                  }`} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-foreground truncate">{notification.zone}</p>
                    <p className="text-xs text-muted-foreground">{notification.message}</p>
                    <p className="text-[10px] text-muted-foreground/60 mt-1">{notification.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
