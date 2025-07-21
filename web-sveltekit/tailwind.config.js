import forms from '@tailwindcss/forms';

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        // Legal Brand Colors
        'legal-primary': '#4F46E5', // indigo-600
        'legal-secondary': '#1E293B', // slate-800  
        'legal-accent': '#8B5CF6', // violet-500
        
        // Professional Grays
        'legal-gray': {
          50: '#F8FAFC',
          100: '#F1F5F9', 
          200: '#E2E8F0',
          300: '#CBD5E1',
          400: '#94A3B8',
          500: '#64748B',
          600: '#475569',
          700: '#334155',
          800: '#1E293B',
          900: '#0F172A'
        },

        // Legal Status Colors
        'legal-success': '#10B981', // emerald-500
        'legal-warning': '#F59E0B', // amber-500  
        'legal-error': '#EF4444', // red-500
        'legal-info': '#3B82F6', // blue-500

        // Traditional Legal Colors
        'legal-gold': '#D97706', // amber-600
        'legal-navy': '#1E3A8A', // blue-800
        'legal-crimson': '#DC2626' // red-600
      },
      
      fontFamily: {
        'legal': ['Inter', 'system-ui', 'sans-serif']
      },

      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem'
      },

      borderRadius: {
        'legal': '0.5rem'
      },

      boxShadow: {
        'legal': '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
        'legal-lg': '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)'
      }
    }
  },
  plugins: [forms]
};