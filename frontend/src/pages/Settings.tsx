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
  Wifi,
  CheckCircle
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { useState } from "react";
import { useAppSettings, getSystemStatus } from "@/hooks/useAppState";
import { exportToJSON } from "@/services/exportService";
import { ResetSettingsDialog } from "@/components/dialogs";

export default function Settings() {
  const { settings, hasChanges, updateSettings, saveSettings, resetToDefaults } = useAppSettings();
  const [showResetDialog, setShowResetDialog] = useState(false);
  const [showSaveSuccess, setShowSaveSuccess] = useState(false);
  const systemStatus = getSystemStatus();

  const handleSaveSettings = () => {
    saveSettings();
    setShowSaveSuccess(true);
    setTimeout(() => setShowSaveSuccess(false), 3000);
  };

  const handleExportData = () => {
    const data = {
      settings,
      systemStatus,
      timestamp: new Date().toISOString(),
    };
    exportToJSON(data);
  };

  const handleBackupNow = () => {
    alert('Backup initiated. This may take a few minutes...\n\nBackup will include all route data, driver information, and system configuration.');
  };

  const handleNotificationToggle = (key: keyof typeof settings.notificationsEnabled) => {
    updateSettings({
      ...settings,
      notificationsEnabled: {
        ...settings.notificationsEnabled,
        [key]: !settings.notificationsEnabled[key],
      },
    });
  };

  const handleSecurityToggle = (key: keyof typeof settings.security) => {
    updateSettings({
      ...settings,
      security: {
        ...settings.security,
        [key]: !settings.security[key],
      },
    });
  };

  return (
    <div className="space-y-6 animate-fade-in max-w-4xl">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground">Settings</h1>
        <p className="text-muted-foreground text-sm mt-1">System configuration and data management</p>
      </div>

      {/* Success Message */}
      {showSaveSuccess && (
        <Card className="glass bg-success/10 border border-success/20">
          <CardContent className="p-4 flex items-center gap-3">
            <CheckCircle className="h-5 w-5 text-success" />
            <span className="text-sm text-success">Settings saved successfully</span>
          </CardContent>
        </Card>
      )}

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
                <p className="text-xs text-success">Connected ({systemStatus.api.latency}ms)</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-4 rounded-lg bg-secondary/50">
              <div className="p-2 rounded-lg bg-success/10">
                <Database className="h-5 w-5 text-success" />
              </div>
              <div>
                <p className="text-sm font-medium text-foreground">Database</p>
                <p className="text-xs text-success">Healthy ({systemStatus.database.size})</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-4 rounded-lg bg-secondary/50">
              <div className="p-2 rounded-lg bg-success/10">
                <HardDrive className="h-5 w-5 text-success" />
              </div>
              <div>
                <p className="text-sm font-medium text-foreground">Storage</p>
                <p className="text-xs text-muted-foreground">{systemStatus.storage.percentage}% used ({systemStatus.storage.used}/{systemStatus.storage.total})</p>
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
            { id: "routeUpdates", label: "Route Updates", description: "Get notified when routes are optimized", key: "routeUpdates" as const },
            { id: "capacityAlerts", label: "Capacity Alerts", description: "Alerts when buses exceed 90% capacity", key: "capacityAlerts" as const },
            { id: "driverStatus", label: "Driver Status Changes", description: "Notifications for driver check-ins", key: "driverStatus" as const },
            { id: "systemHealth", label: "System Health Alerts", description: "Critical system performance notifications", key: "systemHealth" as const },
          ].map((item) => (
            <div key={item.id} className="flex items-center justify-between p-3 rounded-lg hover:bg-secondary/30 transition-colors">
              <div>
                <Label htmlFor={item.id} className="font-medium cursor-pointer">{item.label}</Label>
                <p className="text-xs text-muted-foreground mt-0.5">{item.description}</p>
              </div>
              <Switch 
                id={item.id} 
                checked={settings.notificationsEnabled[item.key]}
                onCheckedChange={() => handleNotificationToggle(item.key)}
              />
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
              <Button variant="outline" className="gap-2" onClick={handleBackupNow}>
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
              <Button variant="outline" className="gap-2" onClick={handleExportData}>
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
              { id: "2fa", label: "Two-Factor Authentication", description: "Require 2FA for admin access", key: "twoFactorAuth" as const },
              { id: "audit", label: "Audit Logging", description: "Log all system changes", key: "auditLogging" as const },
              { id: "session", label: "Auto Session Timeout", description: "Logout after 30 minutes of inactivity", key: "autoSessionTimeout" as const },
            ].map((item) => (
              <div key={item.id} className="flex items-center justify-between p-3 rounded-lg hover:bg-secondary/30 transition-colors">
                <div>
                  <Label htmlFor={item.id} className="font-medium cursor-pointer">{item.label}</Label>
                  <p className="text-xs text-muted-foreground mt-0.5">{item.description}</p>
                </div>
                <Switch 
                  id={item.id}
                  checked={settings.security[item.key]}
                  onCheckedChange={() => handleSecurityToggle(item.key)}
                />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Save Button */}
      <div className="flex justify-end gap-3 pt-4">
        <Button 
          variant="outline"
          onClick={() => setShowResetDialog(true)}
        >
          Reset to Defaults
        </Button>
        <Button 
          className="gap-2 bg-primary hover:bg-primary/90"
          onClick={handleSaveSettings}
          disabled={!hasChanges}
        >
          <Save className="h-4 w-4" />
          Save Changes
        </Button>
      </div>

      {/* Reset Dialog */}
      <ResetSettingsDialog
        isOpen={showResetDialog}
        onOpenChange={setShowResetDialog}
        onConfirm={resetToDefaults}
      />
    </div>
  );
}
