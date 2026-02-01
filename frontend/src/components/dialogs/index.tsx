import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Phone, MessageSquare, LogOut, Settings, User, X, ChevronDown } from 'lucide-react';
import { FilterOptions } from '@/hooks/useAppState';

/**
 * Filter Modal for Routes
 */
export function FilterDialog({
  isOpen,
  onOpenChange,
  onFilter,
  zones = [],
  drivers = [],
}: {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  onFilter: (filters: FilterOptions) => void;
  zones?: string[];
  drivers?: string[];
}) {
  const [filters, setFilters] = useState<FilterOptions>({});

  const handleApply = () => {
    onFilter(filters);
    onOpenChange(false);
  };

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Filter Routes</DialogTitle>
          <DialogDescription>Narrow down your routes by status, zone, or driver</DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Status Filter */}
          <div className="space-y-2">
            <Label>Status</Label>
            <div className="space-y-2">
              {['active', 'pending', 'delayed', 'completed'].map(status => (
                <div key={status} className="flex items-center space-x-2">
                  <Checkbox
                    id={`status-${status}`}
                    checked={filters.status === status}
                    onCheckedChange={() =>
                      setFilters(prev => ({ ...prev, status: filters.status === status ? undefined : status }))
                    }
                  />
                  <Label htmlFor={`status-${status}`} className="capitalize cursor-pointer">
                    {status}
                  </Label>
                </div>
              ))}
            </div>
          </div>

          {/* Zone Filter */}
          {zones.length > 0 && (
            <div className="space-y-2">
              <Label htmlFor="zone-select">Zone</Label>
              <select
                id="zone-select"
                className="w-full px-3 py-2 rounded-lg bg-secondary/50 border border-border text-foreground"
                value={filters.zone || ''}
                onChange={(e) => setFilters(prev => ({ ...prev, zone: e.target.value || undefined }))}
              >
                <option value="">All zones</option>
                {zones.map(zone => (
                  <option key={zone} value={zone}>{zone}</option>
                ))}
              </select>
            </div>
          )}

          {/* Driver Filter */}
          {drivers.length > 0 && (
            <div className="space-y-2">
              <Label htmlFor="driver-select">Driver</Label>
              <select
                id="driver-select"
                className="w-full px-3 py-2 rounded-lg bg-secondary/50 border border-border text-foreground"
                value={filters.driver || ''}
                onChange={(e) => setFilters(prev => ({ ...prev, driver: e.target.value || undefined }))}
              >
                <option value="">All drivers</option>
                {drivers.map(driver => (
                  <option key={driver} value={driver}>{driver}</option>
                ))}
              </select>
            </div>
          )}
        </div>

        <div className="flex gap-2 justify-end pt-4">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleApply} className="bg-primary hover:bg-primary/90">
            Apply Filters
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}

/**
 * Driver Contact Modal
 */
export function DriverContactDialog({
  isOpen,
  onOpenChange,
  driver,
}: {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  driver?: { name: string; phone?: string; email?: string };
}) {
  const [contactMethod, setContactMethod] = useState<'call' | 'sms'>('call');

  const handleContact = () => {
    if (!driver) return;

    if (contactMethod === 'call' && driver.phone) {
      window.location.href = `tel:${driver.phone}`;
    } else if (contactMethod === 'sms' && driver.phone) {
      window.location.href = `sms:${driver.phone}`;
    }

    onOpenChange(false);
  };

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Contact Driver</DialogTitle>
          <DialogDescription>Send a message or call the driver</DialogDescription>
        </DialogHeader>

        {driver && (
          <div className="space-y-4">
            <div className="p-3 rounded-lg bg-secondary/50">
              <p className="font-semibold text-foreground">{driver.name}</p>
              {driver.phone && (
                <p className="text-sm text-muted-foreground mt-1">📱 {driver.phone}</p>
              )}
              {driver.email && (
                <p className="text-sm text-muted-foreground">📧 {driver.email}</p>
              )}
            </div>

            <div className="space-y-3">
              <Label>Contact Method</Label>
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <input
                    type="radio"
                    id="call"
                    name="contact"
                    value="call"
                    checked={contactMethod === 'call'}
                    onChange={() => setContactMethod('call')}
                    className="w-4 h-4"
                  />
                  <Label htmlFor="call" className="flex items-center gap-2 cursor-pointer">
                    <Phone className="h-4 w-4" />
                    Call
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <input
                    type="radio"
                    id="sms"
                    name="contact"
                    value="sms"
                    checked={contactMethod === 'sms'}
                    onChange={() => setContactMethod('sms')}
                    className="w-4 h-4"
                  />
                  <Label htmlFor="sms" className="flex items-center gap-2 cursor-pointer">
                    <MessageSquare className="h-4 w-4" />
                    SMS
                  </Label>
                </div>
              </div>
            </div>

            <div className="flex gap-2 justify-end pt-4">
              <Button variant="outline" onClick={() => onOpenChange(false)}>
                Cancel
              </Button>
              <Button onClick={handleContact} className="bg-primary hover:bg-primary/90">
                Send {contactMethod === 'call' ? 'Call' : 'SMS'}
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}

/**
 * User Profile Dropdown Menu
 */
export function UserProfileMenu() {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" className="gap-2">
          <div className="h-8 w-8 rounded-full bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center">
            <User className="h-4 w-4 text-primary-foreground" />
          </div>
          <div className="hidden md:flex flex-col items-start">
            <span className="text-sm font-medium">Admin</span>
            <span className="text-[10px] text-muted-foreground">Sparrow</span>
          </div>
          <ChevronDown className="h-4 w-4 ml-1" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <DropdownMenuLabel>My Account</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem className="gap-2 cursor-pointer">
          <User className="h-4 w-4" />
          <span>Profile Settings</span>
        </DropdownMenuItem>
        <DropdownMenuItem className="gap-2 cursor-pointer">
          <Settings className="h-4 w-4" />
          <span>Preferences</span>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem className="gap-2 cursor-pointer text-destructive">
          <LogOut className="h-4 w-4" />
          <span>Logout</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

/**
 * Notifications Panel
 */
import { Notification } from '@/hooks/useAppState';

export function NotificationsPanel({
  notifications,
  onMarkAsRead,
  onDismiss,
}: {
  notifications: Notification[];
  onMarkAsRead: (id: string) => void;
  onDismiss: (id: string) => void;
}) {
  return (
    <div className="absolute top-16 right-4 z-[1000] w-96 glass rounded-lg overflow-hidden">
      <div className="p-4 border-b border-border">
        <h3 className="font-semibold text-foreground">Notifications</h3>
      </div>

      <div className="max-h-96 overflow-y-auto">
        {notifications.length === 0 ? (
          <div className="p-4 text-center text-muted-foreground">
            <p>No notifications</p>
          </div>
        ) : (
          <div className="divide-y divide-border">
            {notifications.map(notif => (
              <div
                key={notif.id}
                className={`p-4 cursor-pointer hover:bg-secondary/30 transition-colors ${
                  notif.read ? 'opacity-60' : 'bg-secondary/50'
                }`}
                onClick={() => onMarkAsRead(notif.id)}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1">
                    <p className="font-semibold text-sm text-foreground">{notif.title}</p>
                    <p className="text-xs text-muted-foreground mt-1">{notif.description}</p>
                    <p className="text-xs text-muted-foreground mt-2">
                      {notif.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onDismiss(notif.id);
                    }}
                    className="text-muted-foreground hover:text-foreground"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="p-3 border-t border-border text-center">
        <Button variant="ghost" size="sm" className="text-accent hover:text-accent">
          View All Notifications
        </Button>
      </div>
    </div>
  );
}

/**
 * Reset Settings Confirmation Dialog
 */
export function ResetSettingsDialog({
  isOpen,
  onOpenChange,
  onConfirm,
}: {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: () => void;
}) {
  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Reset to Defaults</DialogTitle>
          <DialogDescription>
            This will reset all settings to their default values. This action cannot be undone.
          </DialogDescription>
        </DialogHeader>

        <div className="flex gap-2 justify-end pt-4">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={() => {
              onConfirm();
              onOpenChange(false);
            }}
          >
            Reset
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
