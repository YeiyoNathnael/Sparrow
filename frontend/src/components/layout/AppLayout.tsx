import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { TopNav } from "./TopNav";

export function AppLayout() {
  return (
    <div className="min-h-screen bg-background flex">
      <Sidebar />
      <div className="flex-1 ml-64 transition-all duration-300">
        <TopNav />
        <main className="p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
