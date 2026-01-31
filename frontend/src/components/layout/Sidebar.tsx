import { NavLink, useLocation } from "react-router-dom";
import { 
  LayoutDashboard, 
  Globe, 
  SlidersHorizontal, 
  FileText, 
  Settings,
  ChevronLeft,
  ChevronRight
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useState } from "react";
import rtaLogo from "@/assets/rta-logo.png";

const navItems = [
  { path: "/", label: "Dashboard", icon: LayoutDashboard },
  { path: "/map", label: "Live Map", icon: Globe },
  { path: "/optimize", label: "Optimization Studio", icon: SlidersHorizontal },
  { path: "/operations", label: "Route Manifest", icon: FileText },
  { path: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside 
      className={cn(
        "fixed left-0 top-0 z-40 h-screen bg-sidebar border-r border-sidebar-border flex flex-col transition-all duration-300",
        collapsed ? "w-20" : "w-64"
      )}
    >
      {/* Logo Section */}
      <div className="h-16 flex items-center px-4 border-b border-sidebar-border">
        <div className="flex items-center gap-3 overflow-hidden">
          <img src={rtaLogo} alt="RTA Logo" className="h-10 w-auto flex-shrink-0" />
          {!collapsed && (
            <div className="flex flex-col">
              <span className="text-lg font-bold text-foreground tracking-tight">RTA Nexus</span>
              <span className="text-[10px] text-muted-foreground uppercase tracking-widest">Mission Control</span>
            </div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={cn(
                "flex items-center gap-3 px-3 py-3 rounded-lg text-sm font-medium transition-all duration-200 group",
                isActive 
                  ? "bg-primary/10 text-primary border border-primary/20" 
                  : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
              )}
            >
              <item.icon 
                className={cn(
                  "h-5 w-5 flex-shrink-0 transition-colors",
                  isActive ? "text-primary" : "text-muted-foreground group-hover:text-accent"
                )} 
              />
              {!collapsed && <span>{item.label}</span>}
              {isActive && !collapsed && (
                <div className="ml-auto h-2 w-2 rounded-full bg-primary pulse-live" />
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Collapse Button */}
      <div className="p-3 border-t border-sidebar-border">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-muted-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground transition-colors"
        >
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          {!collapsed && <span className="text-sm">Collapse</span>}
        </button>
      </div>

      {/* System Status */}
      {!collapsed && (
        <div className="p-4 border-t border-sidebar-border">
          <div className="glass-subtle rounded-lg p-3">
            <div className="flex items-center gap-2 mb-2">
              <div className="h-2 w-2 rounded-full bg-success pulse-live" />
              <span className="text-xs font-medium text-foreground">System Online</span>
            </div>
            <p className="text-[10px] text-muted-foreground">
              Last sync: 2 min ago
            </p>
          </div>
        </div>
      )}
    </aside>
  );
}
