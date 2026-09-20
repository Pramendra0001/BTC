# Frontend Handoff & Architecture

## State Management
We use **TanStack Query** (React Query) for server state.
Local state is handled via standard React `useState` and `useContext` for global auth state.

## API Client
Axios is configured as the base API client in `frontend/src/api/client.ts`.
It automatically intercepts 401 errors to trigger the token refresh flow.

## Component Guidelines
- Use functional components and hooks.
- Styling is implemented using Tailwind CSS.
- Graph visualizations should use a dedicated wrapper component (e.g., `<GraphViewer />`) to isolate Cytoscape.js logic.

## Routing
Managed by React Router.
- `/` -> Dashboard
- `/alerts` -> Alert Queue
- `/alerts/:id` -> Alert Detail & Graph View
- `/cases` -> Case Management
