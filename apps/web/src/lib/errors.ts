/**
 * Centralized error handling for API responses.
 * Transforms backend errors into user-friendly messages.
 */

import { AxiosError } from 'axios';
import { toast } from 'sonner';

interface ApiErrorResponse {
  error?: string;
  message?: string;
  detail?: string;
}

const ERROR_MESSAGES: Record<string, string> = {
  'Invalid RTSP URL format': 'The RTSP URL format is invalid. Please use rtsp://...',
  'Failed to start stream': 'Could not start the stream. Please verify the URL is accessible.',
  'Network Error': 'Unable to connect to the server. Please check your connection.',
  'timeout of': 'The request timed out. Please try again.',
  'ECONNREFUSED': 'Server is not responding. Please ensure the backend is running.',
};

function getReadableMessage(error: unknown): string {
  if (error instanceof AxiosError) {
    const data = error.response?.data as ApiErrorResponse | undefined;
    const backendMessage = data?.error || data?.message || data?.detail;
    
    if (backendMessage) {
      for (const [key, friendly] of Object.entries(ERROR_MESSAGES)) {
        if (backendMessage.includes(key)) {
          return friendly;
        }
      }
      return backendMessage;
    }
    
    if (error.code === 'ECONNABORTED') {
      return 'The request timed out. The stream may take a while to start.';
    }
    
    if (error.code === 'ERR_NETWORK') {
      return ERROR_MESSAGES['Network Error'];
    }
    
    return error.message || 'An unexpected error occurred';
  }
  
  if (error instanceof Error) {
    return error.message;
  }
  
  return 'An unexpected error occurred';
}

export function handleApiError(error: unknown, context?: string): void {
  const message = getReadableMessage(error);
  const title = context ? `${context} failed` : 'Error';
  
  toast.error(title, { description: message });
}

export function createApiError(error: unknown): Error {
  return new Error(getReadableMessage(error));
}

export { getReadableMessage };
