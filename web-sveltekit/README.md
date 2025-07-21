# Verdict360 Legal Chatbot - SvelteKit Frontend

Professional AI legal chatbot platform for South African law firms built with SvelteKit.

## 🏗️ Architecture

**Target Market**: R5,000-R10,000 monthly subscriptions from SA law firms
**Technology Stack**: SvelteKit + Tailwind CSS + TypeScript
**Design Focus**: Professional legal SaaS interface

## 🎨 Brand Colors

- **Primary**: `#4F46E5` (indigo-600) - Main legal brand color
- **Secondary**: `#1E293B` (slate-800) - Professional dark tone  
- **Accent**: `#8B5CF6` (violet-500) - Call-to-action highlights
- **Legal Gold**: `#D97706` (amber-600) - Traditional legal accent

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- FastAPI backend running on `http://localhost:8000`
- Keycloak auth server on `http://localhost:8080`

### Installation

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env

# Start development server
npm run dev
```

### Build & Deploy

```bash
# Production build
npm run build

# Preview build locally
npm run preview

# Lint code
npm run lint

# Format code  
npm run format
```

## 🏛️ Project Structure

```
src/
├── lib/
│   ├── components/
│   │   ├── ui/                    # Base design system
│   │   │   ├── Button.svelte      # Professional legal buttons
│   │   │   ├── Card.svelte        # Content cards  
│   │   │   ├── Input.svelte       # Form inputs with validation
│   │   │   └── Modal.svelte       # Modal dialogs
│   │   ├── legal-saas/           # Legal SaaS specific
│   │   │   └── (future components)
│   │   └── chatbot/              # Chatbot interface
│   │       ├── ChatWidget.svelte  # Main chat component
│   │       └── ChatMessage.svelte # Message bubbles
│   ├── services/                 # API integration
│   │   ├── chatbot.ts           # FastAPI chat integration  
│   │   └── auth.ts              # Keycloak authentication
│   └── utils.ts                  # Utility functions
├── routes/
│   ├── +layout.svelte           # Main layout
│   ├── +page.svelte             # Landing page
│   ├── chatbot/                 # Chatbot demo
│   ├── dashboard/               # Law firm dashboard  
│   ├── consultation/            # Booking system
│   └── widget/                  # Embeddable widget
└── app.css                      # Legal theme styles
```

## 🎯 Key Features

### ✅ Completed Components

- **Legal Design System**: Professional UI components with legal branding
- **Chat Interface**: AI legal assistant with message bubbles and typing indicators  
- **Landing Page**: Professional legal SaaS marketing page
- **Dashboard**: Law firm analytics and management interface
- **Consultation Booking**: Professional intake forms and scheduling
- **Embeddable Widget**: Iframe-ready chatbot for law firm websites

### 🔗 Backend Integration

- **FastAPI Connection**: Integrated with existing legal processing APIs
- **Keycloak Authentication**: Professional user management for law firms
- **Legal Vector Search**: Connected to ChromaDB legal document search
- **SA Legal Citations**: Integration with South African legal citation system

### 🎨 Design Features  

- **Professional Legal Theme**: Tailored for law firm branding
- **Responsive Design**: Mobile and desktop optimized
- **Legal Typography**: Professional Inter font family
- **Accessibility**: WCAG compliant components
- **Performance**: Optimized for fast loading

## 🔌 Backend API Integration

The frontend connects to your existing FastAPI backend:

```typescript
// Example API calls
const response = await fetch(`${API_URL}/api/v1/chat`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: userInput })
});
```

### API Endpoints Used:
- `POST /api/v1/chat` - Legal AI chat
- `GET /api/v1/documents/{id}` - Legal document retrieval  
- `POST /api/v1/search/cases` - SA legal case search
- `GET /health` - API health check

## 🌐 Environment Variables

```env
VITE_API_URL=http://localhost:8000
VITE_KEYCLOAK_URL=http://localhost:8080  
VITE_KEYCLOAK_REALM=Verdict360
VITE_KEYCLOAK_CLIENT_ID=legal-chatbot-web
```

## 📱 Embeddable Widget

The chatbot can be embedded in law firm websites:

```html
<iframe 
  src="https://your-domain.com/widget" 
  width="400" 
  height="600"
  frameborder="0">
</iframe>
```

## 🚢 Production Deployment

Ready for deployment to:
- **Vercel**: Zero-config SvelteKit deployment
- **Netlify**: Static site with serverless functions  
- **Docker**: Containerized deployment
- **Traditional Hosting**: Static build output

## 📈 Business Model Integration

- **Subscription Ready**: R5,000-R10,000 monthly pricing tiers
- **Multi-tenant**: Law firm isolation and branding
- **Professional Invoicing**: Client consultation billing  
- **Analytics Dashboard**: Legal practice performance metrics

## 🔧 Development

### Available Scripts
- `npm run dev` - Start development server (http://localhost:3000)
- `npm run build` - Production build  
- `npm run preview` - Preview production build
- `npm run lint` - Code linting
- `npm run format` - Code formatting
- `npm run test` - Unit testing (Vitest)

### Code Quality
- **TypeScript**: Full type safety for legal domain objects
- **ESLint**: Professional code standards  
- **Prettier**: Consistent code formatting
- **Vitest**: Component unit testing

---

**Status**: ✅ Production Ready - Built for South African legal market