// Mock data that matches the comprehensive backend analytics structure
// Based on the analytics_service.py and endpoints we discovered

export const mockDashboardSummary = {
  period: { start: '2025-06-24', end: '2025-07-24' },
  summary_metrics: {
    total_conversations: 247,
    total_voice_calls: 89,
    consultations_booked: 45,
    conversion_rate: 18.2,
    average_response_time: 2.3,
    client_satisfaction: 4.7,
    legal_accuracy_score: 95.2
  },
  legal_area_breakdown: {
    'criminal': 67,
    'family': 52,
    'commercial': 43,
    'civil': 38,
    'property': 29,
    'employment': 18
  },
  conversion_funnel: {
    chat_initiated: 247,
    consultation_requested: 89,
    consultation_booked: 45,
    consultation_completed: 38,
    retainer_signed: 12
  },
  trending_keywords: [
    { keyword: 'divorce proceedings', legal_area: 'family', mention_count: 23, trending_score: 8.7, growth_rate: 15.2 },
    { keyword: 'criminal charges', legal_area: 'criminal', mention_count: 34, trending_score: 8.2, growth_rate: 12.8 },
    { keyword: 'property transfer', legal_area: 'property', mention_count: 18, trending_score: 7.9, growth_rate: 22.3 },
    { keyword: 'employment dispute', legal_area: 'employment', mention_count: 15, trending_score: 7.4, growth_rate: 8.9 },
    { keyword: 'contract breach', legal_area: 'commercial', mention_count: 21, trending_score: 7.1, growth_rate: 5.4 }
  ],
  channel_breakdown: {
    'web_chat': 158,
    'voice_call': 89
  }
};

export const mockConversationAnalytics = [
  {
    id: 'conv_001',
    conversation_type: 'chat',
    legal_area: 'family',
    duration_seconds: 420,
    total_messages: 12,
    consultation_booked: true,
    started_at: '2025-07-24T09:15:00Z',
    client_satisfaction: 5,
    urgency_level: 'high'
  },
  {
    id: 'conv_002', 
    conversation_type: 'voice',
    legal_area: 'criminal',
    duration_seconds: 680,
    total_messages: 0,
    consultation_booked: true,
    started_at: '2025-07-24T08:30:00Z',
    client_satisfaction: 4,
    urgency_level: 'critical'
  },
  {
    id: 'conv_003',
    conversation_type: 'chat',
    legal_area: 'commercial',
    duration_seconds: 290,
    total_messages: 8,
    consultation_booked: false,
    started_at: '2025-07-24T07:45:00Z',
    client_satisfaction: 3,
    urgency_level: 'normal'
  }
];

export const mockPerformanceMetrics = {
  total_conversations: 247,
  conversion_rate: 18.2,
  average_response_time: 2.3,
  client_satisfaction_avg: 4.2,
  legal_accuracy_score: 95.2,
  peak_hours: ['09:00-10:00', '14:00-15:00', '16:00-17:00'],
  response_time_by_area: {
    'criminal': 1.8,
    'family': 2.1,
    'commercial': 2.5,
    'civil': 2.8,
    'property': 3.2,
    'employment': 2.4
  }
};

export const mockLegalAreaBreakdown = {
  period: { start: '2025-06-24', end: '2025-07-24' },
  breakdown: {
    'criminal': { count: 67, percentage: 27.1, avg_duration: 520 },
    'family': { count: 52, percentage: 21.1, avg_duration: 480 },
    'commercial': { count: 43, percentage: 17.4, avg_duration: 380 },
    'civil': { count: 38, percentage: 15.4, avg_duration: 420 },
    'property': { count: 29, percentage: 11.7, avg_duration: 360 },
    'employment': { count: 18, percentage: 7.3, avg_duration: 340 }
  },
  total_conversations: 247
};

export const mockVoiceCallAnalytics = [
  {
    call_id: 'vc_001',
    client_phone: '+27 11 234 5678',
    duration_seconds: 680,
    legal_area: 'criminal',
    consultation_booked: true,
    escalated_to_human: false,
    call_quality_score: 4.8,
    started_at: '2025-07-24T08:30:00Z',
    transcript_available: true
  },
  {
    call_id: 'vc_002',
    client_phone: '+27 21 567 8901',
    duration_seconds: 420,
    legal_area: 'family',
    consultation_booked: true,
    escalated_to_human: true,
    call_quality_score: 4.2,
    started_at: '2025-07-24T10:15:00Z',
    transcript_available: true
  }
];

export const mockCalendarData = {
  today_schedule: [
    {
      time: '09:00',
      client: 'John Smith',
      legal_area: 'family',
      type: 'consultation',
      duration: 60,
      status: 'confirmed'
    },
    {
      time: '11:00',
      client: 'Sarah Johnson',
      legal_area: 'criminal',
      type: 'consultation',
      duration: 90,
      status: 'pending'
    },
    {
      time: '14:30',
      client: 'Mike Wilson',
      legal_area: 'commercial',
      type: 'consultation',
      duration: 60,
      status: 'confirmed'
    }
  ],
  available_slots: [
    '10:00', '15:00', '16:30'
  ],
  upcoming_availability: {
    'tomorrow': 6,
    'this_week': 23,
    'next_week': 31
  }
};

// South African legal citations for context
export const mockLegalCitations = [
  'Carmichele v Minister of Safety and Security 2001 (4) SA 938 (CC)',
  'S v Makwanyane 1995 (3) SA 391 (CC)',
  'Pharmaceutical Manufacturers Association of SA v President of RSA 2000 (2) SA 674 (CC)',
  'Rail Commuters Action Group v Transnet Ltd t/a Metrorail 2005 (2) SA 359 (CC)'
];

export const mockRecentActivity = [
  {
    timestamp: '2025-07-24T10:30:00Z',
    type: 'consultation_booked',
    details: 'New consultation booked for family law matter',
    client: 'Anonymous Client',
    legal_area: 'family'
  },
  {
    timestamp: '2025-07-24T10:15:00Z',
    type: 'voice_call_completed',
    details: 'Voice consultation completed - escalated to lawyer',
    client: 'Anonymous Client',
    legal_area: 'criminal'
  },
  {
    timestamp: '2025-07-24T09:45:00Z',
    type: 'chat_conversation',
    details: 'Legal advice provided on commercial contract dispute',
    client: 'Anonymous Client',
    legal_area: 'commercial'
  }
];