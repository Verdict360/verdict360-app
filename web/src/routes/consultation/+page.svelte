<script lang="ts">
  import { Calendar, Clock, User, Mail, Phone, MessageSquare } from 'lucide-svelte';
  import Card from '@/lib/components/ui/Card.svelte';
  import Button from '@/lib/components/ui/Button.svelte';
  import Input from '@/lib/components/ui/Input.svelte';
  
  let formData = {
    name: '',
    email: '',
    phone: '',
    legalArea: '',
    urgency: 'normal',
    description: '',
    preferredDate: '',
    preferredTime: ''
  };
  
  let isSubmitting = false;
  
  async function submitConsultation() {
    isSubmitting = true;
    
    try {
      // Call the real API endpoint
      const response = await fetch('/api/v1/consultation/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          client_name: formData.name,
          client_email: formData.email,
          client_phone: formData.phone,
          legal_area: formData.legalArea,
          urgency_level: formData.urgency,
          legal_matter_description: formData.description,
          preferred_date: formData.preferredDate,
          preferred_time: formData.preferredTime
        })
      });

      if (response.ok) {
        const result = await response.json();
        
        // Show success message with consultation details
        alert(`Consultation request submitted successfully! 
        
Consultation ID: ${result.consultation_id}
Estimated Cost: ${result.cost_breakdown?.total_cost ? 'R' + result.cost_breakdown.total_cost.toFixed(2) : 'R850'}
Matched Attorney: ${result.attorney_match?.name || 'TBC'}

We will contact you within 24 hours to confirm your appointment.`);
        
        // Reset form on success
        formData = {
          name: '',
          email: '',
          phone: '',
          legalArea: '',
          urgency: 'normal',
          description: '',
          preferredDate: '',
          preferredTime: ''
        };
      } else {
        // Handle API errors
        const errorData = await response.json();
        alert(`Consultation request failed: ${errorData.detail || 'Please try again later.'}`);
      }
    } catch (error) {
      // Handle network errors
      console.error('Consultation submission error:', error);
      alert('Unable to submit consultation request. Please check your connection and try again.');
    }
    
    isSubmitting = false;
  }
</script>

<svelte:head>
  <title>Book Legal Consultation - Verdict360</title>
  <meta name="description" content="Schedule a professional legal consultation with South African legal experts" />
</svelte:head>

<div class="min-h-screen bg-legal-gray-50">
  <!-- Header -->
  <header class="bg-white border-b border-legal-gray-200">
    <div class="legal-container py-6">
      <div class="text-center">
        <h1 class="text-3xl font-bold text-legal-gray-900">Book Legal Consultation</h1>
        <p class="mt-2 text-legal-gray-600">Connect with qualified South African legal professionals</p>
      </div>
    </div>
  </header>
  
  <!-- Main Content -->
  <main class="py-12">
    <div class="legal-container">
      <div class="max-w-4xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Consultation Form -->
        <div class="lg:col-span-2">
          <Card>
            <h2 class="text-xl font-semibold text-legal-gray-900 mb-6">Consultation Details</h2>
            
            <form on:submit|preventDefault={submitConsultation} class="space-y-6">
              <!-- Personal Information -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  label="Full Name"
                  bind:value={formData.name}
                  required
                  placeholder="Enter your full name"
                />
                
                <Input
                  type="email"
                  label="Email Address"
                  bind:value={formData.email}
                  required
                  placeholder="your.email@example.com"
                />
              </div>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  type="tel"
                  label="Phone Number"
                  bind:value={formData.phone}
                  required
                  placeholder="+27 XX XXX XXXX"
                />
                
                <div class="space-y-1">
                  <label class="block text-sm font-medium text-legal-gray-700">
                    Legal Area <span class="text-legal-error">*</span>
                  </label>
                  <select
                    bind:value={formData.legalArea}
                    required
                    class="input-legal"
                  >
                    <option value="">Select legal area...</option>
                    <option value="constitutional">Constitutional Law</option>
                    <option value="criminal">Criminal Law</option>
                    <option value="civil">Civil Law</option>
                    <option value="commercial">Commercial Law</option>
                    <option value="property">Property Law</option>
                    <option value="family">Family Law</option>
                    <option value="employment">Employment Law</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>
              
              <!-- Urgency -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-legal-gray-700">Urgency Level</label>
                <div class="flex space-x-4">
                  {#each [
                    { value: 'low', label: 'Low - General inquiry', color: 'text-legal-success' },
                    { value: 'normal', label: 'Normal - Standard consultation', color: 'text-legal-primary' },
                    { value: 'high', label: 'High - Urgent legal matter', color: 'text-legal-warning' },
                    { value: 'critical', label: 'Critical - Emergency', color: 'text-legal-error' }
                  ] as option}
                    <label class="flex items-center">
                      <input
                        type="radio"
                        bind:group={formData.urgency}
                        value={option.value}
                        class="mr-2 text-legal-primary focus:ring-legal-primary"
                      />
                      <span class="text-sm {option.color}">{option.label}</span>
                    </label>
                  {/each}
                </div>
              </div>
              
              <!-- Description -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-legal-gray-700">
                  Legal Matter Description <span class="text-legal-error">*</span>
                </label>
                <textarea
                  bind:value={formData.description}
                  required
                  rows="4"
                  class="textarea-legal"
                  placeholder="Please describe your legal matter in detail..."
                ></textarea>
              </div>
              
              <!-- Scheduling -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  type="date"
                  label="Preferred Date"
                  bind:value={formData.preferredDate}
                />
                
                <div class="space-y-1">
                  <label class="block text-sm font-medium text-legal-gray-700">Preferred Time</label>
                  <select bind:value={formData.preferredTime} class="input-legal">
                    <option value="">Select time...</option>
                    <option value="09:00">09:00 AM</option>
                    <option value="10:00">10:00 AM</option>
                    <option value="11:00">11:00 AM</option>
                    <option value="14:00">02:00 PM</option>
                    <option value="15:00">03:00 PM</option>
                    <option value="16:00">04:00 PM</option>
                  </select>
                </div>
              </div>
              
              <!-- Submit -->
              <div class="pt-4">
                <Button
                  type="submit"
                  variant="primary"
                  size="lg"
                  disabled={isSubmitting}
                  class="w-full"
                >
                  {isSubmitting ? 'Submitting...' : 'Book Consultation'}
                </Button>
              </div>
            </form>
          </Card>
        </div>
        
        <!-- Information Sidebar -->
        <div class="space-y-6">
          <!-- Process Info -->
          <Card>
            <h3 class="font-semibold text-legal-gray-900 mb-4">Consultation Process</h3>
            <div class="space-y-4">
              <div class="flex items-start space-x-3">
                <MessageSquare class="h-5 w-5 text-legal-primary mt-0.5" />
                <div class="text-sm text-legal-gray-600">
                  Submit your consultation request with details
                </div>
              </div>
              
              <div class="flex items-start space-x-3">
                <User class="h-5 w-5 text-legal-accent mt-0.5" />
                <div class="text-sm text-legal-gray-600">
                  We match you with a qualified legal expert
                </div>
              </div>
              
              <div class="flex items-start space-x-3">
                <Calendar class="h-5 w-5 text-legal-gold mt-0.5" />
                <div class="text-sm text-legal-gray-600">
                  Schedule your consultation at a convenient time
                </div>
              </div>
            </div>
          </Card>
          
          <!-- Contact Info -->
          <Card>
            <h3 class="font-semibold text-legal-gray-900 mb-4">Contact Information</h3>
            <div class="space-y-3">
              <div class="flex items-center space-x-3">
                <Phone class="h-4 w-4 text-legal-primary" />
                <span class="text-sm text-legal-gray-600">+27 11 123 4567</span>
              </div>
              
              <div class="flex items-center space-x-3">
                <Mail class="h-4 w-4 text-legal-accent" />
                <span class="text-sm text-legal-gray-600">support@verdict360.co.za</span>
              </div>
              
              <div class="flex items-center space-x-3">
                <Clock class="h-4 w-4 text-legal-gold" />
                <span class="text-sm text-legal-gray-600">Mon-Fri: 9AM-5PM</span>
              </div>
            </div>
          </Card>
          
          <!-- Pricing -->
          <Card class="bg-legal-primary/5 border-legal-primary/20">
            <h3 class="font-semibold text-legal-gray-900 mb-2">Consultation Pricing</h3>
            <p class="text-2xl font-bold text-legal-primary">R850</p>
            <p class="text-sm text-legal-gray-600">per hour consultation</p>
            <p class="text-xs text-legal-gray-500 mt-2">
              First 15 minutes free for assessment
            </p>
          </Card>
        </div>
      </div>
    </div>
  </main>
</div>