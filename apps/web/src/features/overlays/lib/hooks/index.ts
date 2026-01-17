import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { getAllOverlays, createOverlay, updateOverlay, deleteOverlay } from '../actions';
import { handleApiError } from '../../../../lib/errors';
import type { Overlay, CreateOverlayDto, UpdateOverlayDto } from '../types';

const OVERLAYS_QUERY_KEY = ['overlays'] as const;

export function useOverlays() {
  return useQuery({
    queryKey: OVERLAYS_QUERY_KEY,
    queryFn: getAllOverlays,
  });
}

export function useCreateOverlay() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createOverlay,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: OVERLAYS_QUERY_KEY });
      toast.success('Overlay created');
    },
    onError: (error) => handleApiError(error, 'Create overlay'),
  });
}

export function useUpdateOverlay() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, updates }: { id: string; updates: UpdateOverlayDto }) =>
      updateOverlay(id, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: OVERLAYS_QUERY_KEY });
    },
    onError: (error) => handleApiError(error, 'Update overlay'),
  });
}

export function useDeleteOverlay(onSuccess?: () => void) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteOverlay,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: OVERLAYS_QUERY_KEY });
      toast.success('Overlay deleted');
      onSuccess?.();
    },
    onError: (error) => handleApiError(error, 'Delete overlay'),
  });
}

export type { Overlay, CreateOverlayDto, UpdateOverlayDto };
