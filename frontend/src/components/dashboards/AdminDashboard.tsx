'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Loader2, Users, MessageSquare, TrendingUp, BarChart3 } from 'lucide-react';

interface AdminStats {
  system_stats: {
    total_users: number;
    total_sessions: number;
    total_messages: number;
    total_profiles: number;
    total_leads: number;
  };
  user_breakdown: {
    by_role: Record<string, number>;
    recent_registrations: number;
  };
  profiling_data: {
    profiles_by_kind: Record<string, number>;
    avg_risk_score: number;
    avg_appetite_score: number;
    risk_distribution: {
      low_risk: number;
      medium_risk: number;
      high_risk: number;
    };
  };
  recent_activity: Array<{
    id: number;
    role: string;
    content: string;
    created_at: string;
    provider: string;
    model: string;
    session_id: string;
  }>;
  top_users: Array<{
    email: string;
    role: string;
    message_count: number;
  }>;
  provider_analytics: Array<{
    provider: string;
    message_count: number;
    avg_latency_ms: number;
    total_tokens_in: number;
    total_tokens_out: number;
  }>;
  public_insights: {
    brisbane_suburbs: string[];
    property_types: string[];
    investment_focus: string[];
    price_ranges: string[];
  };
  recent_registrations: Array<{
    id: number;
    email: string;
    role: string;
    created_at: string;
    company?: string;
  }>;
}

export function AdminDashboard() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const token = localStorage.getItem('aurexus_token');
        const response = await fetch('http://127.0.0.1:8000/api/dashboards/admin', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error('Failed to fetch admin stats');
        }

        const data = await response.json();
        setStats(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load dashboard');
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="text-destructive">Error</CardTitle>
          </CardHeader>
          <CardContent>
            <p>{error}</p>
            <Button onClick={() => window.location.reload()} className="mt-4">
              Retry
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!stats) return null;

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Admin Dashboard</h1>
        <Badge variant="outline">Admin Panel</Badge>
      </div>

      {/* System Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.system_stats.total_users}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Sessions</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.system_stats.total_sessions}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Messages</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.system_stats.total_messages}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Profiles</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.system_stats.total_profiles}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Leads</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.system_stats.total_leads}</div>
          </CardContent>
        </Card>
      </div>

      {/* User Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Users by Role</CardTitle>
            <CardDescription>Distribution of user types</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {Object.entries(stats.user_breakdown.by_role).map(([role, count]) => (
                <div key={role} className="flex justify-between items-center">
                  <span className="capitalize">{role}</span>
                  <Badge variant="secondary">{count}</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Risk Distribution</CardTitle>
            <CardDescription>User risk profile breakdown</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span>Low Risk</span>
                <Badge variant="default">{stats.profiling_data.risk_distribution.low_risk}</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span>Medium Risk</span>
                <Badge variant="secondary">{stats.profiling_data.risk_distribution.medium_risk}</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span>High Risk</span>
                <Badge variant="destructive">{stats.profiling_data.risk_distribution.high_risk}</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>Latest user interactions</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {stats.recent_activity.slice(0, 5).map((activity) => (
              <div key={activity.id} className="flex items-start space-x-4 p-4 border rounded-lg">
                <div className="flex-1">
                  <p className="text-sm text-muted-foreground">
                    {activity.role === 'user' ? 'User' : 'Assistant'} • {activity.provider} • {activity.model}
                  </p>
                  <p className="mt-1">{activity.content}</p>
                  <p className="text-xs text-muted-foreground mt-2">
                    {new Date(activity.created_at).toLocaleString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Public Insights */}
      <Card>
        <CardHeader>
          <CardTitle>Public Market Insights</CardTitle>
          <CardDescription>Popular topics and trends</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <h4 className="font-medium mb-2">Brisbane Suburbs</h4>
              <div className="flex flex-wrap gap-1">
                {stats.public_insights.brisbane_suburbs.map((suburb) => (
                  <Badge key={suburb} variant="outline">{suburb}</Badge>
                ))}
              </div>
            </div>
            <div>
              <h4 className="font-medium mb-2">Property Types</h4>
              <div className="flex flex-wrap gap-1">
                {stats.public_insights.property_types.map((type) => (
                  <Badge key={type} variant="outline">{type}</Badge>
                ))}
              </div>
            </div>
            <div>
              <h4 className="font-medium mb-2">Investment Focus</h4>
              <div className="flex flex-wrap gap-1">
                {stats.public_insights.investment_focus.map((focus) => (
                  <Badge key={focus} variant="outline">{focus}</Badge>
                ))}
              </div>
            </div>
            <div>
              <h4 className="font-medium mb-2">Price Ranges</h4>
              <div className="flex flex-wrap gap-1">
                {stats.public_insights.price_ranges.map((range) => (
                  <Badge key={range} variant="outline">{range}</Badge>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

