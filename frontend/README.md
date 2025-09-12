# Aurexus Public AI - Frontend

A modern, responsive React frontend for the Aurexus Public AI real estate intelligence platform.

## 🚀 Features

### **Modern Chat Interface**
- **Real-time Chat**: Live conversation with AI providers
- **Message History**: Persistent chat sessions
- **Typing Indicators**: Visual feedback during AI responses
- **Error Handling**: Graceful error states and retry functionality

### **AI Provider Management**
- **9 Provider Support**: Mock, OpenAI, Anthropic, Google, Mistral, Cohere, OpenRouter, Perplexity, AWS Bedrock
- **Easy Switching**: Dropdown selector for different AI providers
- **Provider Status**: Visual indicators for available/unavailable providers
- **Real-time Switching**: Change providers without losing conversation

### **Responsive Design**
- **Mobile-First**: Optimized for all screen sizes
- **Touch-Friendly**: Gesture support for mobile devices
- **Accessible**: WCAG compliant with keyboard navigation
- **Modern UI**: Clean, professional design with smooth animations

### **Real Estate Focused**
- **Topic Classification**: Visual indicators for different topics
- **Guardrail Messages**: Clear feedback for out-of-scope questions
- **Performance Metrics**: Display provider latency and token usage
- **Context Awareness**: Smart suggestions and topic guidance

## 🛠️ Tech Stack

- **Framework**: Next.js 15 with App Router
- **UI Library**: React 19 with TypeScript
- **Styling**: Tailwind CSS 4
- **Icons**: Lucide React
- **State Management**: React Hooks (useState, useEffect)
- **HTTP Client**: Native Fetch API
- **Build Tool**: Turbopack (Next.js)

## 📦 Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## 🔧 Configuration

### Environment Variables

Create a `.env.local` file:

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

### Backend Integration

The frontend connects to the Aurexus backend API:

- **Chat Endpoint**: `POST /public/chat`
- **Provider Switching**: Via localStorage (future: backend endpoint)
- **Session Management**: UUID-based session tracking

## 🎨 UI Components

### **ChatInterface**
Main chat container with message history and input.

```tsx
<ChatInterface />
```

### **Message**
Individual chat message with metadata display.

```tsx
<Message message={chatMessage} />
```

### **ChatInput**
Message input with auto-resize and send functionality.

```tsx
<ChatInput 
  onSendMessage={handleSendMessage}
  isLoading={isLoading}
  disabled={hasError}
/>
```

### **ProviderSelector**
AI provider selection dropdown.

```tsx
<ProviderSelector
  selectedProvider={provider}
  onProviderChange={handleProviderChange}
/>
```

## 🔄 State Management

### **Chat State**
```typescript
interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  selectedProvider: string;
  sessionId: string;
}
```

### **Message Types**
```typescript
interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  topic?: string;
  allowed?: boolean;
  provider?: string;
  model?: string;
  tokens_in?: number;
  tokens_out?: number;
  latency_ms?: number;
}
```

## 🎯 User Experience

### **Welcome Flow**
1. User lands on clean, professional interface
2. Welcome message explains capabilities
3. Provider selector shows available options
4. Clear topic guidance for real estate focus

### **Chat Flow**
1. User types message in auto-resizing input
2. Message appears instantly with user avatar
3. Loading indicator shows AI is thinking
4. AI response appears with metadata (provider, latency, tokens)
5. Error handling with retry options

### **Provider Switching**
1. Click provider dropdown in header
2. Select new provider from list
3. Provider switches immediately
4. Future messages use new provider

## 📱 Responsive Design

### **Desktop (1024px+)**
- Full-width chat interface
- Side-by-side layout
- Rich metadata display
- Hover effects and animations

### **Tablet (768px - 1023px)**
- Optimized chat width
- Touch-friendly controls
- Condensed metadata
- Swipe gestures

### **Mobile (< 768px)**
- Full-screen chat
- Large touch targets
- Simplified interface
- Keyboard-friendly input

## 🎨 Design System

### **Colors**
- **Primary**: Blue (#3B82F6)
- **Success**: Green (#10B981)
- **Warning**: Amber (#F59E0B)
- **Error**: Red (#EF4444)
- **Neutral**: Gray scale

### **Typography**
- **Font**: Geist Sans (system fallback)
- **Headings**: Bold, clear hierarchy
- **Body**: Readable, comfortable line height
- **Code**: Geist Mono

### **Spacing**
- **Consistent**: 4px base unit
- **Padding**: 12px, 16px, 24px
- **Margins**: 8px, 16px, 24px, 32px
- **Gaps**: 8px, 12px, 16px

## 🔧 Development

### **File Structure**
```
src/
├── app/                 # Next.js App Router
│   ├── layout.tsx      # Root layout
│   ├── page.tsx        # Home page
│   └── globals.css     # Global styles
├── components/         # React components
│   └── chat/          # Chat-specific components
├── lib/               # Utilities
│   ├── api.ts         # API client
│   └── utils.ts       # Helper functions
└── types/             # TypeScript types
    └── chat.ts        # Chat-related types
```

### **Key Features**
- **TypeScript**: Full type safety
- **ESLint**: Code quality and consistency
- **Tailwind**: Utility-first CSS
- **Responsive**: Mobile-first design
- **Accessible**: WCAG compliance

## 🚀 Deployment

### **Vercel (Recommended)**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Set environment variables
vercel env add NEXT_PUBLIC_API_URL
```

### **Docker**
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

### **Environment Variables**
- `NEXT_PUBLIC_API_URL`: Backend API URL
- `NODE_ENV`: Environment (development/production)

## 🔗 Backend Integration

### **API Endpoints**
- `POST /public/chat`: Send message and get AI response
- `GET /health`: Health check (future)
- `POST /providers/switch`: Switch AI provider (future)

### **Request Format**
```typescript
interface ChatRequest {
  session_id: string;
  message: string;
  source: string;
  consent_data_usage: boolean;
  consent_contact: boolean;
}
```

### **Response Format**
```typescript
interface ChatResponse {
  session_id: string;
  answer: string;
  topic: string;
  allowed: boolean;
}
```

## 🎯 Future Enhancements

### **Planned Features**
- [ ] Real-time provider switching via backend
- [ ] Message search and filtering
- [ ] Export chat history
- [ ] Dark mode toggle
- [ ] Voice input/output
- [ ] File upload support
- [ ] Advanced analytics dashboard
- [ ] Multi-language support

### **Performance Optimizations**
- [ ] Message virtualization for long chats
- [ ] Image optimization
- [ ] Code splitting
- [ ] Service worker for offline support
- [ ] CDN integration

## 🐛 Troubleshooting

### **Common Issues**

#### Frontend won't start
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run dev
```

#### Backend connection failed
- Check `NEXT_PUBLIC_API_URL` is correct
- Ensure backend is running on port 8000
- Check CORS settings in backend

#### Provider switching not working
- Check localStorage in browser dev tools
- Verify provider IDs match backend
- Clear localStorage and try again

### **Debug Mode**
```bash
# Enable debug logging
NODE_ENV=development npm run dev
```

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

**Built with ❤️ by the Aurexus team**