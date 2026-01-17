---
applyTo: '**'
---

# Frontend Design Instructions

**RTSP Livestream Overlay Web Application**

## Design System Overview

This document defines the UI/UX rules that AI agents must follow when building the frontend for the RTSP Livestream Overlay Web Application.

The interface prioritizes **clarity, control, and real-time feedback** over visual complexity.

---

## 1. Design Philosophy & Brand Guidelines

### Design Approach

* **Design philosophy:** Functional Minimalism
* **Core principles:**

  * Clarity over decoration
  * Real-time feedback for user actions
  * Predictable, low-friction interactions
  * Accessibility and keyboard support by default

This is a **tool**, not a showcase. Every UI element must earn its place.

### Brand Identity

* **Brand personality:** Technical, reliable, unobtrusive
* **Target audience:**

  * Technical users (developers, testers, reviewers)
  * Comfortable with developer tools and dashboards
* **Tone of voice:** Clear, concise, neutral, instructional

---

## 2. Color System

### Primary Colors

```css
--color-primary: #2563EB; /* Blue – primary actions */
--color-primary-light: #3B82F6;
--color-primary-dark: #1E40AF;
--color-primary-contrast: #FFFFFF;
```

### Secondary Colors

```css
--color-secondary: #10B981; /* Green – success / live state */
--color-secondary-light: #34D399;
--color-secondary-dark: #059669;
--color-secondary-contrast: #FFFFFF;
```

### Neutral Colors

```css
--color-neutral-50: #F9FAFB;
--color-neutral-100: #F3F4F6;
--color-neutral-200: #E5E7EB;
--color-neutral-300: #D1D5DB;
--color-neutral-400: #9CA3AF;
--color-neutral-500: #6B7280;
--color-neutral-600: #4B5563;
--color-neutral-700: #374151;
--color-neutral-800: #1F2937;
--color-neutral-900: #111827;
```

### Semantic Colors

```css
--color-success: #10B981;
--color-warning: #F59E0B;
--color-error: #EF4444;
--color-info: #3B82F6;
```

### Background & Surface

```css
--color-background: #F9FAFB;
--color-surface: #FFFFFF;
--color-surface-elevated: #FFFFFF;
```

### Text Colors

```css
--color-text-primary: #111827;
--color-text-secondary: #4B5563;
--color-text-disabled: #9CA3AF;
--color-text-inverse: #FFFFFF;
```

### Color Usage Rules

* Primary color: main CTAs (Play Stream, Save Overlay)
* Secondary color: live/active indicators
* Error color: validation errors, delete actions
* Overlays must remain readable over video backgrounds

---

## 3. Typography

### Font Families

```css
--font-primary: Inter, system-ui, sans-serif;
--font-heading: Inter, system-ui, sans-serif;
--font-mono: JetBrains Mono, monospace;
```

### Typography Rules

* Maximum of **one font family**
* Strong hierarchy, no decorative fonts
* Overlay text must remain legible at small sizes

---

## 4. Spacing & Layout

### Layout Structure

* Main layout:

  * **Video canvas** (center / left)
  * **Overlay control panel** (right sidebar)
* Sidebar must never overlap the video

### Component Spacing Rules

* Internal padding: `16px`
* Space between controls: `12–16px`
* Sidebar width: `320–360px`

---

## 5. Responsive Design

### Breakpoints

```css
--breakpoint-sm: 640px;
--breakpoint-md: 768px;
--breakpoint-lg: 1024px;
```

### Responsive Rules

* Desktop-first design
* Mobile support is **functional**, not optimized
* On small screens:

  * Sidebar collapses below video
  * Overlays still draggable

---

## 6. Component Design Patterns

### Video Player

* Must clearly indicate:

  * Playing
  * Paused
  * Error state
* Controls:

  * Play / Pause
  * Volume
* No autoplay without user interaction

### Overlay Components (Critical)

**Overlay elements must:**

* Be draggable using mouse
* Be resizable using visible handles
* Show bounding box when selected
* Snap visually without animation lag
* Update position immediately on drag

Overlay selection rules:

* Click selects overlay
* Selected overlay shows resize handles
* Clicking outside deselects

### Overlay Control Panel

* List all overlays
* Allow:

  * Create
  * Edit text / image URL
  * Delete
* Highlight currently selected overlay

---

## 7. Forms & Inputs

### RTSP URL Input

* Always visible
* Clear label: “RTSP Stream URL”
* Validation feedback required
* Disable Play button until valid input

### Overlay Forms

* Text overlay:

  * Text content
  * Font size
* Image overlay:

  * Image URL
* Save changes explicitly (no auto-save)

---

## 8. Modals & Confirmations

* Confirm before deleting overlays
* Modal rules:

  * ESC to close
  * Focus trapped
  * Clear primary action

---

## 9. Loading & Real-Time Feedback

### Required States

* Stream connecting
* Stream error
* Overlay save in progress
* Overlay delete success/failure

Never leave the user guessing.

---

## 10. Accessibility (a11y)

### Mandatory

* Keyboard draggable overlays (arrow keys)
* Focus indicators visible
* Buttons and inputs labeled
* 4.5:1 contrast minimum
* Screen reader labels for controls

---

## 11. Animation & Motion

* Minimal motion
* No heavy transitions on video or overlays
* Dragging overlays must feel immediate
* Respect `prefers-reduced-motion`

---

## 12. Iconography

* Icon set: **Lucide react**
* Use icons sparingly
* Always pair icon-only buttons with aria-labels

---

## 13. Error Handling UX

* Errors must:

  * Be inline
  * Be specific
  * Explain how to fix
* Example:

  > “Unable to connect to RTSP stream. Check the URL or stream availability.”

---

## 14. Empty & Initial States

### Initial Load

* No stream loaded
* Prompt to enter RTSP URL

### No Overlays

* Empty overlay list message:

  > “No overlays yet! Add one to get started.”

---

## 15. Performance Considerations

* Avoid unnecessary re-renders while dragging
* Overlays rendered using absolute positioning
* No expensive layout recalculations on move

---

## 16. Component Library using shadcn/ui (Minimum Required)

* Button
* Input
* Select
* Card
* Modal
* Alert
* Sidebar
* OverlayBox (custom component)

---

## 17. Design Review Checklist

Before marking UI complete:

* [ ] Stream plays correctly
* [ ] Overlays drag smoothly
* [ ] Overlays resize correctly
* [ ] CRUD actions visible and clear
* [ ] No layout overlap with video
* [ ] Accessible via keyboard
* [ ] Errors handled visibly
* [ ] No unnecessary visual noise


## 20. Data Fetching & API Integration

### Data Fetching Strategy
- **Data Fetching Library:** Tanstack Query
- **API Client:** Fetch API
- **Base URL Management:** Use environment variables for API endpoints

### API Client Configuration
- Create a centralized API client for CRUD operations.
```

### Data Fetching Pattern

#### Pattern: Using Tanstack Query (Recommended)
```typescript
// hooks/useUsers.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api/client';

interface User {
  id: number;
  name: string;
  email: string;
}

// Fetch users list
export function useUsers() {
  return useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      const { data } = await apiClient.get<User[]>('/users');
      return data;
    },
    staleTime: 5 * 60 * 1000, // Consider data fresh for 5 minutes
    gcTime: 10 * 60 * 1000, // Keep in cache for 10 minutes
  });
}

// Fetch single user
export function useUser(userId: number) {
  return useQuery({
    queryKey: ['users', userId],
    queryFn: async () => {
      const { data } = await apiClient.get<User>(`/users/${userId}`);
      return data;
    },
    enabled: !!userId, // Only run if userId is provided
  });
}

// Create user mutation
export function useCreateUser() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (newUser: Omit<User, 'id'>) => {
      const { data } = await apiClient.post<User>('/users', newUser);
      return data;
    },
    onSuccess: () => {
      // Invalidate and refetch users list
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}

// Update user mutation
export function useUpdateUser() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, ...updates }: Partial<User> & { id: number }) => {
      const { data } = await apiClient.put<User>(`/users/${id}`, updates);
      return data;
    },
    onSuccess: (data) => {
      // Update specific user in cache
      queryClient.setQueryData(['users', data.id], data);
      // Invalidate users list
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}

// Delete user mutation
export function useDeleteUser() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (userId: number) => {
      await apiClient.delete(`/users/${userId}`);
      return userId;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}
```

---

## 17. Caching Strategies

### Client-Side Caching Layers

#### 1. In-Memory Cache (Tanstack Query)
```typescript
// React Query configuration
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
      retry: 3,
      refetchOnWindowFocus: false,
      refetchOnMount: true,
      refetchOnReconnect: true,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <YourApp />
    </QueryClientProvider>
  );
}
```


### Caching Strategies by Data Type

#### Static/Reference Data (Rarely Changes)
```typescript
// Cache aggressively - 1 hour or more
export function useCountries() {
  return useQuery({
    queryKey: ['countries'],
    queryFn: fetchCountries,
    staleTime: 60 * 60 * 1000, // 1 hour
    gcTime: 24 * 60 * 60 * 1000, // 24 hours
  });
}
```

#### User Profile Data (Changes Occasionally)
```typescript
// Cache moderately - 5-15 minutes
export function useUserProfile() {
  return useQuery({
    queryKey: ['user', 'profile'],
    queryFn: fetchUserProfile,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
```

#### Real-Time Data (Changes Frequently)
```typescript
// Minimal caching or polling
export function useRealtimeData() {
  return useQuery({
    queryKey: ['realtime'],
    queryFn: fetchRealtimeData,
    staleTime: 0, // Always consider stale
    refetchInterval: 5000, // Poll every 5 seconds
  });
}
```

#### List/Collection Data with Pagination
```typescript
export function useUsersPaginated(page: number, limit: number) {
  return useQuery({
    queryKey: ['users', 'paginated', page, limit],
    queryFn: () => fetchUsers(page, limit),
    staleTime: 2 * 60 * 1000, // 2 minutes
    keepPreviousData: true, // Keep previous page while fetching new one
  });
}
```

---

## 18. Optimistic Updates

### Implementing Optimistic UI
```typescript
// Optimistic update pattern
export function useTodoToggle() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (todoId: number) => {
      await apiClient.patch(`/todos/${todoId}/toggle`);
    },
    onMutate: async (todoId) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['todos'] });

      // Snapshot previous value
      const previousTodos = queryClient.getQueryData<Todo[]>(['todos']);

      // Optimistically update cache
      queryClient.setQueryData<Todo[]>(['todos'], (old) =>
        old?.map((todo) =>
          todo.id === todoId ? { ...todo, completed: !todo.completed } : todo
        )
      );

      // Return context with snapshot
      return { previousTodos };
    },
    onError: (err, todoId, context) => {
      // Rollback on error
      queryClient.setQueryData(['todos'], context?.previousTodos);
    },
    onSettled: () => {
      // Refetch after mutation
      queryClient.invalidateQueries({ queryKey: ['todos'] });
    },
  });
}

// Usage in component
function TodoItem({ todo }: { todo: Todo }) {
  const toggleMutation = useTodoToggle();

  return (
    <div>
      <input
        type="checkbox"
        checked={todo.completed}
        onChange={() => toggleMutation.mutate(todo.id)}
        disabled={toggleMutation.isPending}
      />
      <span>{todo.title}</span>
    </div>
  );
}
```

---

## 19. Prefetching & Background Refetching

### Prefetching Data
```typescript
// Prefetch on hover
function UserListItem({ user }: { user: User }) {
  const queryClient = useQueryClient();

  const prefetchUserDetails = () => {
    queryClient.prefetchQuery({
      queryKey: ['users', user.id],
      queryFn: () => fetchUserDetails(user.id),
      staleTime: 5 * 60 * 1000,
    });
  };

  return (
    <Link
      to={`/users/${user.id}`}
      onMouseEnter={prefetchUserDetails}
      onFocus={prefetchUserDetails}
    >
      {user.name}
    </Link>
  );
}

// Prefetch on route entry
function Dashboard() {
  const queryClient = useQueryClient();

  useEffect(() => {
    // Prefetch likely next pages
    queryClient.prefetchQuery({
      queryKey: ['notifications'],
      queryFn: fetchNotifications,
    });
  }, [queryClient]);

  return <DashboardContent />;
}
```

### Background Refetching
```typescript
// Automatic background refetch
export function useUserStats() {
  return useQuery({
    queryKey: ['user', 'stats'],
    queryFn: fetchUserStats,
    staleTime: 1 * 60 * 1000, // 1 minute
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes in background
    refetchIntervalInBackground: true, // Continue refetching when tab is inactive
  });
}
```

---

## 20. Real-Time Data Integration

### WebSocket Integration
```typescript
// hooks/useWebSocket.ts
import { useEffect, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';

export function useWebSocket(url: string) {
  const [isConnected, setIsConnected] = useState(false);
  const queryClient = useQueryClient();

  useEffect(() => {
    const ws = new WebSocket(url);

    ws.onopen = () => {
      setIsConnected(true);
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);

      // Update cache based on message type
      switch (message.type) {
        case 'USER_UPDATED':
          queryClient.setQueryData(
            ['users', message.data.id],
            message.data
          );
          queryClient.invalidateQueries({ queryKey: ['users'] });
          break;

        case 'NEW_NOTIFICATION':
          queryClient.setQueryData<Notification[]>(
            ['notifications'],
            (old) => [message.data, ...(old || [])]
          );
          break;

        default:
          break;
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      setIsConnected(false);
      console.log('WebSocket disconnected');
    };

    return () => {
      ws.close();
    };
  }, [url, queryClient]);

  return { isConnected };
}

// Usage
function App() {
  const { isConnected } = useWebSocket('wss://api.example.com/ws');

  return (
    <div>
      <ConnectionIndicator isConnected={isConnected} />
      <YourApp />
    </div>
  );
}
```

### Server-Sent Events (SSE)
```typescript
// hooks/useSSE.ts
import { useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';

export function useServerSentEvents(url: string) {
  const queryClient = useQueryClient();

  useEffect(() => {
    const eventSource = new EventSource(url);

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      // Update relevant queries
      queryClient.invalidateQueries({ queryKey: ['realtime-data'] });
    };

    eventSource.onerror = (error) => {
      console.error('SSE error:', error);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [url, queryClient]);
}
```

---

## 21. Error Handling & Retry Logic

### Global Error Handling
```typescript
// Configure global error handling
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, error: any) => {
        // Don't retry on 4xx errors
        if (error.response?.status >= 400 && error.response?.status < 500) {
          return false;
        }
        // Retry up to 3 times for other errors
        return failureCount < 3;
      },
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    },
  },
});

// Custom error boundary for queries
function QueryErrorBoundary({ children }: { children: React.ReactNode }) {
  return (
    <ErrorBoundary
      FallbackComponent={ErrorFallback}
      onError={(error, errorInfo) => {
        // Log to error tracking service
        console.error('Query error:', error, errorInfo);
      }}
    >
      {children}
    </ErrorBoundary>
  );
}
```

### Per-Query Error Handling
```typescript
export function useUsers() {
  return useQuery({
    queryKey: ['users'],
    queryFn: fetchUsers,
    retry: 2,
    retryDelay: 1000,
    onError: (error: any) => {
      // Handle specific errors
      if (error.response?.status === 404) {
        toast.error('Users not found');
      } else if (error.response?.status === 500) {
        toast.error('Server error. Please try again later.');
      } else {
        toast.error('An error occurred while fetching users');
      }
    },
  });
}

// In component
function UserList() {
  const { data, isLoading, error, refetch } = useUsers();

  if (isLoading) return <LoadingSpinner />;
  
  if (error) {
    return (
      <ErrorState
        message="Failed to load users"
        onRetry={refetch}
      />
    );
  }

  return <UserGrid users={data} />;
}
```

---

## 22. Request Cancellation

### Canceling In-Flight Requests
```typescript
// Automatic cancellation with React Query
export function useSearchUsers(searchTerm: string) {
  return useQuery({
    queryKey: ['users', 'search', searchTerm],
    queryFn: async ({ signal }) => {
      // Pass AbortSignal to axios
      const { data } = await apiClient.get('/users/search', {
        params: { q: searchTerm },
        signal, // Automatic cancellation
      });
      return data;
    },
    enabled: searchTerm.length > 2, // Only search if term is long enough
  });
}

// Manual cancellation
function SearchUsers() {
  const [searchTerm, setSearchTerm] = useState('');
  const queryClient = useQueryClient();

  const handleSearch = (value: string) => {
    // Cancel previous search
    queryClient.cancelQueries({ queryKey: ['users', 'search'] });
    setSearchTerm(value);
  };

  const { data } = useSearchUsers(searchTerm);

  return (
    <input
      type="text"
      value={searchTerm}
      onChange={(e) => handleSearch(e.target.value)}
    />
  );
}
```

---

## 23. Pagination & Infinite Scroll

### Traditional Pagination
```typescript
export function useUsersPaginated(page: number) {
  return useQuery({
    queryKey: ['users', 'paginated', page],
    queryFn: () => fetchUsers({ page, limit: 20 }),
    keepPreviousData: true, // Keep showing old data while fetching new page
  });
}

function UserListPaginated() {
  const [page, setPage] = useState(1);
  const { data, isLoading, isPreviousData } = useUsersPaginated(page);

  return (
    <>
      <UserGrid users={data?.users} isLoading={isPreviousData} />
      <Pagination
        currentPage={page}
        totalPages={data?.totalPages}
        onPageChange={setPage}
      />
    </>
  );
}
```

### Infinite Scroll
```typescript
export function useUsersInfinite() {
  return useInfiniteQuery({
    queryKey: ['users', 'infinite'],
    queryFn: ({ pageParam = 1 }) => fetchUsers({ page: pageParam, limit: 20 }),
    getNextPageParam: (lastPage, allPages) => {
      // Return next page number or undefined if no more pages
      return lastPage.hasMore ? allPages.length + 1 : undefined;
    },
    initialPageParam: 1,
  });
}

function UserListInfinite() {
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useUsersInfinite();

  const { ref, inView } = useInView();

  useEffect(() => {
    if (inView && hasNextPage) {
      fetchNextPage();
    }
  }, [inView, fetchNextPage, hasNextPage]);

  return (
    <>
      {data?.pages.map((page) =>
        page.users.map((user) => <UserCard key={user.id} user={user} />)
      )}
      <div ref={ref}>
        {isFetchingNextPage && <LoadingSpinner />}
      </div>
    </>
  );
}
```

---

## 24. Request Debouncing & Throttling

### Debouncing Search Requests
```typescript
import { useDebounce } from 'use-debounce';

function SearchUsers() {
  const [searchInput, setSearchInput] = useState('');
  const [debouncedSearch] = useDebounce(searchInput, 500); // 500ms delay

  const { data, isLoading } = useQuery({
    queryKey: ['users', 'search', debouncedSearch],
    queryFn: () => searchUsers(debouncedSearch),
    enabled: debouncedSearch.length > 2,
  });

  return (
    <>
      <input
        type="text"
        value={searchInput}
        onChange={(e) => setSearchInput(e.target.value)}
        placeholder="Search users..."
      />
      {isLoading && <span>Searching...</span>}
      {data && <SearchResults results={data} />}
    </>
  );
}
```

### Throttling API Calls
```typescript
import { throttle } from 'lodash';

function LivePreview() {
  const updatePreview = throttle(async (content: string) => {
    await apiClient.post('/preview', { content });
  }, 1000); // Max once per second

  return (
    <textarea
      onChange={(e) => updatePreview(e.target.value)}
    />
  );
}
```

---

## 25. Data Synchronization

### Sync State Across Tabs
```typescript
// Using BroadcastChannel API
const channel = new BroadcastChannel('app-sync');

export function useCrossTabSync() {
  const queryClient = useQueryClient();

  useEffect(() => {
    channel.onmessage = (event) => {
      if (event.data.type === 'INVALIDATE_CACHE') {
        queryClient.invalidateQueries({ queryKey: event.data.queryKey });
      }
    };

    return () => {
      channel.close();
    };
  }, [queryClient]);

  const broadcastInvalidation = (queryKey: string[]) => {
    channel.postMessage({ type: 'INVALIDATE_CACHE', queryKey });
  };

  return { broadcastInvalidation };
}
```

### Sync with Backend (Polling)
```typescript
export function usePolling<T>(
  queryKey: string[],
  queryFn: () => Promise<T>,
  interval: number = 30000 // 30 seconds
) {
  return useQuery({
    queryKey,
    queryFn,
    refetchInterval: interval,
    refetchIntervalInBackground: false, // Stop when tab inactive
  });
}
```

---

## 26. Backend Integration Best Practices

### API Service Layer Organization
```typescript
// services/userService.ts
import { apiClient } from '../api/client';

export const userService = {
  async getAll(): Promise<User[]> {
    const { data } = await apiClient.get('/users');
    return data;
  },

  async getById(id: number): Promise<User> {
    const { data } = await apiClient.get(`/users/${id}`);
    return data;
  },

  async create(user: CreateUserDto): Promise<User> {
    const { data } = await apiClient.post('/users', user);
    return data;
  },

  async update(id: number, updates: UpdateUserDto): Promise<User> {
    const { data } = await apiClient.put(`/users/${id}`, updates);
    return data;
  },

  async delete(id: number): Promise<void> {
    await apiClient.delete(`/users/${id}`);
  },

  async search(query: string): Promise<User[]> {
    const { data } = await apiClient.get('/users/search', {
      params: { q: query },
    });
    return data;
  },
};
```

### Type-Safe API Integration
```typescript
// types/api.ts
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  metadata?: {
    timestamp: string;
    requestId: string;
  };
}

export interface PaginatedResponse<T> {
  data: T[];
  page: number;
  limit: number;
  total: number;
  totalPages: number;
  hasMore: boolean;
}

// Usage with React Query
export function useUsers() {
  return useQuery<ApiResponse<User[]>>({
    queryKey: ['users'],
    queryFn: async () => {
      const { data } = await apiClient.get<ApiResponse<User[]>>('/users');
      return data;
    },
    select: (response) => response.data, // Extract just the data
  });
}
```

### Handling Different Response Formats
```typescript
// Transform API responses to frontend format
export function useProducts() {
  return useQuery({
    queryKey: ['products'],
    queryFn: fetchProducts,
    select: (data) => {
      // Transform backend format to frontend format
      return data.map((product) => ({
        id: product.id,
        name: product.product_name, // Snake_case to camelCase
        price: product.price / 100, // Convert cents to dollars
        inStock: product.stock_quantity > 0,
        createdAt: new Date(product.created_at),
      }));
    },
  });
}
```

---

## Data Fetching Checklist

When implementing data fetching:
- [ ] Use appropriate caching strategy for data type
- [ ] Implement loading states
- [ ] Implement error states with retry option
- [ ] Implement empty states
- [ ] Add request cancellation for searches
- [ ] Debounce search inputs
- [ ] Use optimistic updates for better UX
- [ ] Implement pagination or infinite scroll for lists
- [ ] Add prefetching for predictable navigation
- [ ] Configure appropriate stale times
- [ ] Handle authentication errors (401)
- [ ] Handle authorization errors (403)
- [ ] Invalidate cache after mutations
- [ ] Test offline behavior
- [ ] Monitor and log API errors

---


---

## Notes for AI Agent

- Always refer to this design system when building UI components
- Maintain consistency across all interfaces
- Ask clarifying questions if design requirements are ambiguous
- Suggest improvements if you identify UX issues
- Flag any accessibility concerns
- Ensure all interactive elements have appropriate states (hover, active, focus, disabled)
- Prioritize user experience and accessibility over aesthetics alone
- Always implement proper loading and error states
- Use appropriate caching strategies based on data freshness requirements
- Prefer optimistic updates for better perceived performance
- Implement request cancellation to avoid race conditions
- Use type-safe API integration with TypeScript
- Follow the project's chosen data fetching pattern consistently
- Consider mobile/slow network scenarios
- Test with network throttling enabled
- Only add high-level comments, that describes the code block, what it does and how it's used, and prevent verbose nested comments.
---