import { MobileNav } from "@/components/layout/MobileNav";
import { DesktopSidebar } from "@/components/layout/DesktopSidebar";
import { TopBar } from "@/components/layout/TopBar";

export default function LegalDashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen flex-col">
      {/* Mobile Navigation - Only visible on small screens */}
      <div className="md:hidden">
        <MobileNav />
      </div>

      <div className="flex flex-1 flex-col md:flex-row">
        {/* Desktop Sidebar - Hidden on mobile */}
        <div className="hidden md:flex md:w-64 md:flex-col md:fixed md:inset-y-0 z-[80] bg-card border-r">
          <DesktopSidebar />
        </div>

        {/* Main Content Area */}
        <div className="flex-1 md:pl-64">
          <TopBar />
          <main className="flex-1 p-4 sm:p-6 lg:p-8">
            {children}
          </main>
        </div>
      </div>
    </div>
  );
}
