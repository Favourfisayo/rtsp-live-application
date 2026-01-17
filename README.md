# my-better-t-app

* FFMPEG Command for ref: `ffmpeg -re -stream_loop -1 -i "C:\Users\HP\Videos\Aeon Flux 2005 REMASTERED 1080p BluRay HEVC x265 5.1 BONE.mkv"  -c copy -f rtsp rtsp://localhost:8554/test`

This project was created with [Better-T-Stack](https://github.com/AmanVarshney01/create-better-t-stack), a modern TypeScript stack that combines React, React Router, and more.

## Features

- **TypeScript** - For type safety and improved developer experience
- **React Router** - Declarative routing for React
- **TailwindCSS** - Utility-first CSS for rapid UI development
- **shadcn/ui** - Reusable UI components
- **Turborepo** - Optimized monorepo build system

## Getting Started

First, install the dependencies:

```bash
pnpm install
```

Then, run the development server:

```bash
pnpm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser to see the web application.

## Project Structure

```
my-better-t-app/
├── apps/
│   ├── web/         # Frontend application (React + React Router)
```

## Available Scripts

- `pnpm run dev`: Start all applications in development mode
- `pnpm run build`: Build all applications
- `pnpm run dev:web`: Start only the web application
- `pnpm run check-types`: Check TypeScript types across all apps
