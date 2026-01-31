import { 
  Settings as SettingsIcon, 
  Database, 
  Bell, 
  Shield, 
  Palette,
  Globe,
  Clock,
  Save,
  RefreshCw,
  Cpu,
  HardDrive,
  Wifi
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";

export default function Settings() {
  return (
    <div className="space-y-6 animate-fade-in max-w-4xl">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground">Settings</h1>
        <p className="text-muted-foreground text-sm mt-1">System configuration and data management</p>
      </div>

      {/* System Status */}
      <Card className="glass">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Cpu className="h-5 w-5 text-accent" />
            System Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center gap-3 p-4 rounded-lg bg-secondary/50">
              <div className="p-2 rounded-lg bg-success/10">
                <Wifi className="h-5 w-5 text-success" />
              </div>
              <div>
                <p className="text-sm font-medium text-foreground">API Connection</p>
                <p className="text-xs text-success">Connected</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-4 rounded-lg bg-secondary/50">
              <div className="p-2 rounded-lg bg-success/10">
                <Database className="h-5 w-5 text-success" />
              </div>
              <div>
                <p className="text-sm font-medium text-foreground">Database</p>
                <p className="text-xs text-success">Healthy (2.4GB)</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-4 rounded-lg bg-secondary/50">
              <div className="p-2 rounded-lg bg-success/10">
                <HardDrive className="h-5 w-5 text-success" />
              </div>
              <div>
                <p className="text-sm font-medium text-foreground">Storage</p>
                <p className="text-xs text-muted-foreground">68% used (34GB/50GB)</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Notifications */}
      <Card className="glass">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5 text-accent" />
            Notifications
          </CardTitle>
          <CardDescription>Configure alert preferences</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {[
            { id: "route-updates", label: "Route Updates", description: "Get notified when routes are optimized", defaultChecked: true },
            { id: "capacity-alerts", label: "Capacity Alerts", description: "Alerts when buses exceed 90% capacity", defaultChecked: true },
            { id: "driver-status", label: "Driver Status Changes", description: "Notifications for driver check-ins", defaultChecked: false },
            { id: "system-health", label: "System Health Alerts", description: "Critical system performance notifications", defaultChecked: true },
          ].map((item) => (
            <div key={item.id} className="flex items-center justify-between p-3 rounded-lg hover:bg-secondary/30 transition-colors">
              <div>
                <Label htmlFor={item.id} className="font-medium cursor-pointer">{item.label}</Label>
                <p className="text-xs text-muted-foreground mt-0.5">{item.description}</p>
              </div>
              <Switch id={item.id} defaultChecked={item.defaultChecked} />
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Regional Settings */}
      <Card className="glass">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Globe className="h-5 w-5 text-accent" />
            Regional Settings
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-lg bg-secondary/50">
              <div className="flex items-center gap-2 mb-2">
                <Clock className="h-4 w-4 text-muted-foreground" />
                <Label className="font-medium">Timezone</Label>
              </div>
              <p className="text-foreground">Gulf Standard Time (GMT+4)</p>
              <p className="text-xs text-muted-foreground mt-1">Dubai, United Arab Emirates</p>
            </div>
            <div className="p-4 rounded-lg bg-secondary/50">
              <div className="flex items-center gap-2 mb-2">
                <Palette className="h-4 w-4 text-muted-foreground" />
                <Label className="font-medium">Theme</Label>
              </div>
              <p className="text-foreground">Dark Mode</p>
              <p className="text-xs text-muted-foreground mt-1">Mission Control optimized</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Data Management */}
      <Card className="glass">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5 text-accent" />
            Data Management
          </CardTitle>
          <CardDescription>Manage system data and backups</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 rounded-lg bg-secondary/50">
              <div>
                <p className="font-medium text-foreground">Last Backup</p>
                <p className="text-sm text-muted-foreground">January 31, 2026 at 02:00 AM GST</p>
              </div>
              <Button variant="outline" className="gap-2">
                <RefreshCw className="h-4 w-4" />
                Backup Now
              </Button>
            </div>
            
            <Separator />
            
            <div className="flex items-center justify-between p-4 rounded-lg bg-secondary/50">
              <div>
                <p className="font-medium text-foreground">Export All Data</p>
                <p className="text-sm text-muted-foreground">Download complete system data as JSON</p>
              </div>
              <Button variant="outline" className="gap-2">
                <Save className="h-4 w-4" />
                Export
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Security */}
      <Card className="glass">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-accent" />
            Security
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[
              { id: "2fa", label: "Two-Factor Authentication", description: "Require 2FA for admin access", defaultChecked: true },
              { id: "audit", label: "Audit Logging", description: "Log all system changes", defaultChecked: true },
              { id: "session", label: "Auto Session Timeout", description: "Logout after 30 minutes of inactivity", defaultChecked: false },
            ].map((item) => (
              <div key={item.id} className="flex items-center justify-between p-3 rounded-lg hover:bg-secondary/30 transition-colors">
                <div>
                  <Label htmlFor={item.id} className="font-medium cursor-pointer">{item.label}</Label>
                  <p className="text-xs text-muted-foreground mt-0.5">{item.description}</p>
                </div>
                <Switch id={item.id} defaultChecked={item.defaultChecked} />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Save Button */}
      <div className="flex justify-end gap-3 pt-4">
        <Button variant="outline">Reset to Defaults</Button>
        <Button className="gap-2 bg-primary hover:bg-primary/90">
          <Save className="h-4 w-4" />
          Save Changes
        </Button>
      </div>
    </div>
  );
}
