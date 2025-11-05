# Dispatcher Agents Frontend

Frontend application for the Voice Agent Conversation System.

## Setup

### Prerequisites
- Node.js 18+ and npm

### Installation

```bash
cd frontend
npm install
```

### Running the Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Environment Variables

Create a `.env.local` file:
```
VITE_API_BASE_URL=http://localhost:8000
```

### Building for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Project Structure

```
frontend/
├── src/
│   ├── components/       # React components
│   ├── services/         # API services
│   ├── types/            # TypeScript type definitions
│   ├── App.tsx           # Main app component
│   ├── main.tsx          # Entry point
│   └── index.css         # Global styles
├── public/               # Static assets
├── package.json
└── vite.config.ts
```

## Development

- Run `npm run dev` for development mode with hot reload
- Run `npm run build` to build for production
- Run `npm run preview` to preview production build

