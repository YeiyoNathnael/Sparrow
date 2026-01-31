import { Bell, Search, User, Wifi } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export function TopNav() {
  return (
    <header className="h-16 bg-card/40 backdrop-blur-xl border-b border-border flex items-center justify-between px-6">
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
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5 text-muted-foreground" />
          <span className="absolute -top-0.5 -right-0.5 h-4 w-4 rounded-full bg-primary text-[10px] font-bold text-primary-foreground flex items-center justify-center">
            3
          </span>
        </Button>

        {/* User Profile */}
        <Button variant="ghost" className="gap-2">
          <div className="h-8 w-8 rounded-full bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center">
            <User className="h-4 w-4 text-primary-foreground" />
          </div>
          <div className="hidden md:flex flex-col items-start">
            <span className="text-sm font-medium">Admin</span>
            <span className="text-[10px] text-muted-foreground">RTA Dubai</span>
          </div>
        </Button>
      </div>
    </header>
  );
}
