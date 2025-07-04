'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
// Charts temporarily disabled for build fix
// import { 
//   XAxis, 
//   YAxis, 
//   CartesianGrid, 
//   Tooltip, 
//   ResponsiveContainer,
//   PieChart,
//   Pie,
//   Cell,
//   Area,
//   AreaChart
// } from 'recharts';
import { 
  Users, 
  MessageSquare, 
  FileText, 
  TrendingUp, 
  Clock,
  CheckCircle,
  AlertTriangle,
  Scale,
  RefreshCw
} from 'lucide-react';

interface SystemStats {
  totalUsers: number;
  activeUsers: number;
  totalQueries: number;
  totalDocuments: number;
  vectorStoreSize: number;
  systemHealth: 'healthy' | 'warning' | 'critical';
  uptime: string;
  lastUpdated: string;
}

interface QueryAnalytics {
  period: string;
  queries: number;
  responses: number;
  avgConfidence: number;
  avgResponseTime: number;
}

interface LegalPracticeArea {
  area: string;
  queries: number;
  percentage: number;
  color: string;
}

interface UserActivity {
  userId: string;
  name: string;
  firm: string;
  queriesCount: number;
  lastActive: string;
  role: 'attorney' | 'paralegal' | 'staff';
}

interface QualityMetrics {
  citationAccuracy: number;
  responseRelevance: number;
  legalTermAccuracy: number;
  sourceAttribution: number;
}

const COLORS = ['#2563eb', '#dc2626', '#059669', '#d97706', '#7c3aed', '#db2777'];

export default function LegalAdminDashboard() {
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null);
  const [queryAnalytics, setQueryAnalytics] = useState<QueryAnalytics[]>([]);
  const [practiceAreas, setPracticeAreas] = useState<LegalPracticeArea[]>([]);
  const [userActivity, setUserActivity] = useState<UserActivity[]>([]);
  const [qualityMetrics, setQualityMetrics] = useState<QualityMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [lastRefresh, setLastRefresh] = useState(new Date());

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setIsLoading(true);
    try {
      // Simulate API calls - in production these would be real endpoints
      await Promise.all([
        loadSystemStats(),
        loadQueryAnalytics(),
        loadPracticeAreas(),
        loadUserActivity(),
        loadQualityMetrics()
      ]);
      setLastRefresh(new Date());
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadSystemStats = async () => {
    // Mock data - would fetch from /api/admin/system-stats
    const stats: SystemStats = {
      totalUsers: 47,
      activeUsers: 23,
      totalQueries: 1247,
      totalDocuments: 156,
      vectorStoreSize: 2.4, // GB
      systemHealth: 'healthy',
      uptime: '99.7%',
      lastUpdated: new Date().toISOString()
    };
    setSystemStats(stats);
  };

  const loadQueryAnalytics = async () => {
    // Mock data - would fetch from /api/admin/query-analytics
    const analytics: QueryAnalytics[] = [
      { period: 'Mon', queries: 45, responses: 43, avgConfidence: 0.87, avgResponseTime: 2.3 },
      { period: 'Tue', queries: 67, responses: 65, avgConfidence: 0.91, avgResponseTime: 2.1 },
      { period: 'Wed', queries: 89, responses: 86, avgConfidence: 0.89, avgResponseTime: 2.4 },
      { period: 'Thu', queries: 73, responses: 71, avgConfidence: 0.93, avgResponseTime: 1.9 },
      { period: 'Fri', queries: 91, responses: 89, avgConfidence: 0.88, avgResponseTime: 2.2 },
      { period: 'Sat', queries: 34, responses: 33, avgConfidence: 0.85, avgResponseTime: 2.0 },
      { period: 'Sun', queries: 28, responses: 27, avgConfidence: 0.90, avgResponseTime: 1.8 }
    ];
    setQueryAnalytics(analytics);
  };

  const loadPracticeAreas = async () => {
    // Mock data - would fetch from /api/admin/practice-areas
    const areas: LegalPracticeArea[] = [
      { area: 'Contract Law', queries: 234, percentage: 35, color: COLORS[0] },
      { area: 'Labour Law', queries: 178, percentage: 27, color: COLORS[1] },
      { area: 'Constitutional Law', queries: 112, percentage: 17, color: COLORS[2] },
      { area: 'Commercial Law', queries: 89, percentage: 13, color: COLORS[3] },
      { area: 'Criminal Law', queries: 53, percentage: 8, color: COLORS[4] }
    ];
    setPracticeAreas(areas);
  };

  const loadUserActivity = async () => {
    // Mock data - would fetch from /api/admin/user-activity
    const activity: UserActivity[] = [
      { userId: '1', name: 'Sarah Johnson', firm: 'Johnson & Associates', queriesCount: 89, lastActive: '2 hours ago', role: 'attorney' },
      { userId: '2', name: 'Michael Chen', firm: 'Legal Solutions Inc', queriesCount: 67, lastActive: '4 hours ago', role: 'attorney' },
      { userId: '3', name: 'Emma Williams', firm: 'Williams Law Firm', queriesCount: 45, lastActive: '1 hour ago', role: 'paralegal' },
      { userId: '4', name: 'David Miller', firm: 'Corporate Legal', queriesCount: 34, lastActive: '6 hours ago', role: 'attorney' },
      { userId: '5', name: 'Lisa Brown', firm: 'Brown & Partners', queriesCount: 28, lastActive: '3 hours ago', role: 'staff' }
    ];
    setUserActivity(activity);
  };

  const loadQualityMetrics = async () => {
    // Mock data - would fetch from /api/admin/quality-metrics
    const metrics: QualityMetrics = {
      citationAccuracy: 0.92,
      responseRelevance: 0.88,
      legalTermAccuracy: 0.94,
      sourceAttribution: 0.90
    };
    setQualityMetrics(metrics);
  };

  const handleRefresh = () => {
    loadDashboardData();
  };

  const getHealthStatus = (health: string) => {
    switch (health) {
      case 'healthy':
        return { icon: 'CheckCircle', color: 'text-green-600', bg: 'bg-green-100' };
      case 'warning':
        return { icon: 'AlertTriangle', color: 'text-yellow-600', bg: 'bg-yellow-100' };
      case 'critical':
        return { icon: 'AlertTriangle', color: 'text-red-600', bg: 'bg-red-100' };
      default:
        return { icon: 'CheckCircle', color: 'text-gray-600', bg: 'bg-gray-100' };
    }
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'attorney': return 'bg-blue-100 text-blue-800';
      case 'paralegal': return 'bg-green-100 text-green-800';
      case 'staff': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center space-x-2">
          <RefreshCw className="h-6 w-6 animate-spin" />
          <span>Loading dashboard...</span>
        </div>
      </div>
    );
  }

  const healthStatus = systemStats ? getHealthStatus(systemStats.systemHealth) : null;

  return (
    <div className="space-y-4 md:space-y-6">
      {/* Header with refresh */}
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
        <div className="flex items-center space-x-2">
          <Scale className="h-5 w-5 md:h-6 md:w-6 text-primary" />
          <span className="text-base md:text-lg font-semibold">Legal System Analytics</span>
        </div>
        <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
          <span className="text-xs md:text-sm text-muted-foreground">
            Last updated: {lastRefresh.toLocaleTimeString()}
          </span>
          <Button variant="outline" onClick={handleRefresh} size="sm" className="w-fit">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* System Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{systemStats?.totalUsers}</div>
            <p className="text-xs text-muted-foreground">
              {systemStats?.activeUsers} active today
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Legal Queries</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{systemStats?.totalQueries}</div>
            <p className="text-xs text-muted-foreground">
              +12% from last week
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Documents</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{systemStats?.totalDocuments}</div>
            <p className="text-xs text-muted-foreground">
              {systemStats?.vectorStoreSize} GB indexed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">System Health</CardTitle>
            {healthStatus && (
              <div className={`h-4 w-4 ${healthStatus.color}`}>
                {healthStatus.icon === 'CheckCircle' && <CheckCircle className="h-4 w-4" />}
                {healthStatus.icon === 'AlertTriangle' && <AlertTriangle className="h-4 w-4" />}
              </div>
            )}
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold capitalize">{systemStats?.systemHealth}</div>
            <p className="text-xs text-muted-foreground">
              {systemStats?.uptime} uptime
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Query Analytics Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Weekly Query Analytics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-300 flex items-center justify-center">
            <p className="text-muted-foreground">Chart visualization placeholder</p>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Practice Areas */}
        <Card>
          <CardHeader>
            <CardTitle>Legal Practice Areas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-250 flex items-center justify-center">
              <p className="text-muted-foreground">Pie chart visualization placeholder</p>
            </div>
          </CardContent>
        </Card>

        {/* Quality Metrics */}
        <Card>
          <CardHeader>
            <CardTitle>Legal Response Quality</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {qualityMetrics && Object.entries(qualityMetrics).map(([key, value]) => (
              <div key={key} className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="capitalize">{key.replace(/([A-Z])/g, ' $1').trim()}</span>
                  <span className="font-medium">{(value * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-primary h-2 rounded-full transition-all duration-300" 
                    style={{ width: `${value * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* User Activity Table */}
      <Card>
        <CardHeader>
          <CardTitle>Active Legal Professionals</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {userActivity.map((user) => (
              <div key={user.userId} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className="h-10 w-10 bg-primary/10 rounded-full flex items-center justify-center">
                    <Users className="h-4 w-4 text-primary" />
                  </div>
                  <div>
                    <p className="font-medium">{user.name}</p>
                    <p className="text-sm text-muted-foreground">{user.firm}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <Badge className={getRoleColor(user.role)}>
                    {user.role}
                  </Badge>
                  <div className="text-right">
                    <p className="text-sm font-medium">{user.queriesCount} queries</p>
                    <p className="text-xs text-muted-foreground">Active {user.lastActive}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Response Time</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">2.1s</div>
            <p className="text-xs text-muted-foreground">
              -0.3s from last week
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Confidence</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">89.2%</div>
            <p className="text-xs text-muted-foreground">
              +2.1% from last week
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">97.8%</div>
            <p className="text-xs text-muted-foreground">
              +0.5% from last week
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}