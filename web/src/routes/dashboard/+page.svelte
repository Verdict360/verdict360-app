<script lang="ts">
  import { onMount } from 'svelte';
  import Card from '@/lib/components/ui/Card.svelte';
  import Button from '@/lib/components/ui/Button.svelte';
  import { 
    mockDashboardSummary, 
    mockConversationAnalytics, 
    mockPerformanceMetrics,
    mockVoiceCallAnalytics,
    mockRecentActivity,
    mockCalendarData
  } from '$lib/services/mockData.js';
  
  let dashboardData = mockDashboardSummary;
  let recentConversations = mockConversationAnalytics;
  let performanceMetrics = mockPerformanceMetrics;
  let voiceCalls = mockVoiceCallAnalytics;
  let recentActivity = mockRecentActivity;
  let calendarData = mockCalendarData;
  let loading = false;
  
  onMount(async () => {
    // In the future, this will call: api.getDashboardSummary()
    loading = false;
  });

  function formatDuration(seconds: number): string {
    const minutes = Math.floor(seconds / 60);
    return `${minutes}:${(seconds % 60).toString().padStart(2, '0')}`;
  }

  function formatTime(dateString: string): string {
    return new Date(dateString).toLocaleTimeString('en-ZA', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  }
</script>

<svelte:head>
  <title>Dashboard - Verdict360</title>
  <meta name="description" content="Legal practice management dashboard" />
</svelte:head>

<!-- Page Header -->
<div class="bg-white border-b border-legal-gray-200">
  <div class="legal-container py-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-legal-gray-900">Legal Dashboard</h1>
        <p class="text-legal-gray-600">Manage your legal practice with AI assistance</p>
      </div>
      
      <div class="flex items-center space-x-4">
        <Button variant="accent" size="md" class="flex items-center space-x-2">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
          </svg>
          <span>Emergency Consult</span>
        </Button>
        
        <Button variant="outline" size="md">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3"/>
            <path d="M12 1v6m0 6v6m11-7h-6m-6 0H1m5.636-5.636l4.242 4.242m4.243 4.243l4.242 4.242M7.757 16.243l4.242-4.242m4.243-4.243l4.242-4.242"/>
          </svg>
        </Button>
      </div>
    </div>
  </div>
</div>

<!-- Main Content -->
<main class="py-8">
  <div class="legal-container">
      <!-- Primary Metrics Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card class="text-center">
          <div class="flex items-center justify-center mb-3">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#1E40AF" stroke-width="2">
              <path d="M20 2H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h4l4 4 4-4h4a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2z"/>
            </svg>
          </div>
          <div class="text-3xl font-bold text-legal-gray-900">{dashboardData.summary_metrics.total_conversations}</div>
          <div class="text-sm text-legal-gray-600">Total Conversations</div>
          <div class="text-xs text-green-600 mt-1">+12% from last month</div>
        </Card>
        
        <Card class="text-center">
          <div class="flex items-center justify-center mb-3">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2">
              <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
            </svg>
          </div>
          <div class="text-3xl font-bold text-legal-gray-900">{dashboardData.summary_metrics.total_voice_calls}</div>
          <div class="text-sm text-legal-gray-600">Voice Consultations</div>
          <div class="text-xs text-green-600 mt-1">+8% from last month</div>
        </Card>
        
        <Card class="text-center">
          <div class="flex items-center justify-center mb-3">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#D97706" stroke-width="2">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
              <line x1="16" y1="2" x2="16" y2="6"/>
              <line x1="8" y1="2" x2="8" y2="6"/>
              <line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
          </div>
          <div class="text-3xl font-bold text-legal-gray-900">{dashboardData.summary_metrics.consultations_booked}</div>
          <div class="text-sm text-legal-gray-600">Consultations Booked</div>
          <div class="text-xs text-green-600 mt-1">{dashboardData.summary_metrics.conversion_rate}% conversion</div>
        </Card>

        <Card class="text-center">
          <div class="flex items-center justify-center mb-3">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#DC2626" stroke-width="2">
              <polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"/>
            </svg>
          </div>
          <div class="text-3xl font-bold text-legal-gray-900">{dashboardData.summary_metrics.client_satisfaction}</div>
          <div class="text-sm text-legal-gray-600">Client Satisfaction</div>
          <div class="text-xs text-legal-gray-500 mt-1">out of 5 stars</div>
        </Card>
      </div>

      <!-- Legal Areas Breakdown -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <Card>
          <h3 class="text-lg font-semibold text-legal-gray-900 mb-4">Legal Area Distribution</h3>
          <div class="space-y-3">
            {#each Object.entries(dashboardData.legal_area_breakdown) as [area, count]}
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-3">
                  <div class="w-3 h-3 rounded-full bg-legal-blue-500"></div>
                  <span class="text-sm font-medium text-legal-gray-700 capitalize">{area.replace('_', ' ')}</span>
                </div>
                <div class="flex items-center space-x-2">
                  <span class="text-sm text-legal-gray-600">{count} cases</span>
                  <span class="text-xs text-legal-gray-500">({Math.round(count / dashboardData.summary_metrics.total_conversations * 100)}%)</span>
                </div>
              </div>
            {/each}
          </div>
        </Card>

        <Card>
          <h3 class="text-lg font-semibold text-legal-gray-900 mb-4">Trending Legal Keywords</h3>
          <div class="space-y-3">
            {#each dashboardData.trending_keywords as keyword}
              <div class="flex items-center justify-between">
                <div>
                  <div class="text-sm font-medium text-legal-gray-900">{keyword.keyword}</div>
                  <div class="text-xs text-legal-gray-500 capitalize">{keyword.legal_area} • {keyword.mention_count} mentions</div>
                </div>
                <div class="flex items-center space-x-2">
                  <div class="text-xs font-medium text-green-600">+{keyword.growth_rate}%</div>
                  <div class="w-2 h-2 rounded-full bg-green-500"></div>
                </div>
              </div>
            {/each}
          </div>
        </Card>
      </div>
      
      <!-- Recent Activity & Voice Analytics -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <!-- Recent Activity -->
        <Card>
          <h3 class="text-lg font-semibold text-legal-gray-900 mb-4">Recent Activity</h3>
          <div class="space-y-3">
            {#each recentActivity as activity}
              <div class="flex items-start space-x-3 p-3 bg-legal-gray-50 rounded-legal">
                <div class="flex-shrink-0 mt-1">
                  {#if activity.type === 'consultation_booked'}
                    <div class="w-2 h-2 rounded-full bg-green-500"></div>
                  {:else if activity.type === 'voice_call_completed'}
                    <div class="w-2 h-2 rounded-full bg-blue-500"></div>
                  {:else}
                    <div class="w-2 h-2 rounded-full bg-orange-500"></div>
                  {/if}
                </div>
                <div class="flex-1">
                  <div class="text-sm font-medium text-legal-gray-900">{activity.details}</div>
                  <div class="text-xs text-legal-gray-500 capitalize">{activity.legal_area} • {formatTime(activity.timestamp)}</div>
                </div>
              </div>
            {/each}
          </div>
        </Card>

        <!-- Voice Call Analytics -->
        <Card>
          <h3 class="text-lg font-semibold text-legal-gray-900 mb-4">Voice Call Analytics</h3>
          <div class="space-y-3">
            {#each voiceCalls as call}
              <div class="flex items-center justify-between p-3 bg-legal-gray-50 rounded-legal">
                <div class="flex items-center space-x-3">
                  <div class="flex-shrink-0">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2">
                      <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
                    </svg>
                  </div>
                  <div>
                    <div class="text-sm font-medium text-legal-gray-900 capitalize">{call.legal_area} Law</div>
                    <div class="text-xs text-legal-gray-500">
                      {formatDuration(call.duration_seconds)} • {formatTime(call.started_at)}
                      {#if call.escalated_to_human}
                        • Escalated
                      {/if}
                    </div>
                  </div>
                </div>
                <div class="flex items-center space-x-2">
                  <div class="text-xs font-medium text-legal-gray-600">★ {call.call_quality_score}</div>
                  {#if call.consultation_booked}
                    <div class="w-2 h-2 rounded-full bg-green-500"></div>
                  {/if}
                </div>
              </div>
            {/each}
          </div>
        </Card>
      </div>

      <!-- Today's Schedule & Performance -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Today's Schedule -->
        <Card>
          <h3 class="text-lg font-semibold text-legal-gray-900 mb-4">Today's Schedule</h3>
          <div class="space-y-3">
            {#each calendarData.today_schedule as appointment}
              <div class="flex items-center justify-between p-3 border border-legal-gray-200 rounded-legal">
                <div class="flex items-center space-x-3">
                  <div class="text-sm font-medium text-legal-gray-900">{appointment.time}</div>
                  <div>
                    <div class="text-sm font-medium text-legal-gray-900">{appointment.client}</div>
                    <div class="text-xs text-legal-gray-500 capitalize">{appointment.legal_area} • {appointment.duration} min</div>
                  </div>
                </div>
                <div class="flex items-center space-x-2">
                  <span class="px-2 py-1 text-xs rounded-full {appointment.status === 'confirmed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}">{appointment.status}</span>
                </div>
              </div>
            {/each}
          </div>
        </Card>

        <!-- Performance Metrics -->
        <Card>
          <h3 class="text-lg font-semibold text-legal-gray-900 mb-4">Performance Metrics</h3>
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <span class="text-sm text-legal-gray-600">Legal Accuracy Score</span>
              <span class="text-lg font-semibold text-legal-gray-900">{performanceMetrics.legal_accuracy_score}%</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-legal-gray-600">Average Response Time</span>
              <span class="text-lg font-semibold text-legal-gray-900">{performanceMetrics.average_response_time}s</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-legal-gray-600">Client Satisfaction</span>
              <span class="text-lg font-semibold text-legal-gray-900">{performanceMetrics.client_satisfaction_avg}/5</span>
            </div>
            <div class="mt-4">
              <h4 class="text-sm font-medium text-legal-gray-900 mb-2">Peak Hours</h4>
              <div class="flex flex-wrap gap-2">
                {#each performanceMetrics.peak_hours as hour}
                  <span class="px-2 py-1 text-xs bg-legal-blue-100 text-legal-blue-800 rounded-full">{hour}</span>
                {/each}
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  </main>