import { Metadata } from "next";
import LegalAdminDashboard from "@/components/admin/LegalAdminDashboard";

export const metadata: Metadata = {
  title: "Admin Dashboard | Verdict360",
  description: "Administrative dashboard for legal system analytics and monitoring",
};

export default function AdminDashboardPage() {
  return (
    <div className="container mx-auto py-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-primary">Legal System Administration</h1>
        <p className="text-muted-foreground mt-2">
          Monitor system performance, user activity, and legal query analytics for your Verdict360 deployment.
        </p>
      </div>
      
      <LegalAdminDashboard />
    </div>
  );
}