import { Bell, Search, Wifi } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { UserProfileMenu, NotificationsPanel } from "@/components/dialogs";
import { useNotifications } from "@/hooks/useAppState";
import { useState } from "react";

export function TopNav() {
  const [showNotifications, setShowNotifications] = useState(false);
  const { notifications, unreadCount, markAsRead, dismissNotification } = useNotifications();

  return (
    <header className="h-16 bg-card/40 backdrop-blur-xl border-b border-border flex items-center justify-between px-6 relative">
      {/* Search */}
      <div className="flex items-center gap-4 flex-1 max-w-md">
        <div className="relative w-full">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input 
            placeholder="Search routes, zones, buses..." 
            className="pl-10 bg-secondary/50 border-border/50 focus:border-accent/50 focus:ring-accent/20"
          />
        </div>
      </div>

      {/* Right Section */}
      <div className="flex items-center gap-4">
        {/* Live Status */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-success/10 border border-success/20">
          <Wifi className="h-3.5 w-3.5 text-success" />
          <span className="text-xs font-medium text-success">LIVE</span>
        </div>

        {/* Notifications */}
        <div className="relative">
          <Button 
            variant="ghost" 
            size="icon" 
            className="relative"
            onClick={() => setShowNotifications(!showNotifications)}
          >
            <Bell className="h-5 w-5 text-muted-foreground" />
            {unreadCount > 0 && (
              <span className="absolute -top-0.5 -right-0.5 h-4 w-4 rounded-full bg-primary text-[10px] font-bold text-primary-foreground flex items-center justify-center">
                {unreadCount}
              </span>
            )}
          </Button>
          {showNotifications && (
            <NotificationsPanel
              notifications={notifications}
              onMarkAsRead={markAsRead}
              onDismiss={dismissNotification}
            />
          )}
        </div>

        {/* User Profile */}
        <UserProfileMenu />
      </div>
    </header>
  );
}
