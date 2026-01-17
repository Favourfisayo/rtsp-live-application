/**
 * Overlay API actions - handles all overlay-related API calls.
 */

import { apiClient } from '../../../../lib/api-client';
import type { Overlay, CreateOverlayDto, UpdateOverlayDto } from '../types';

export async function getAllOverlays(): Promise<Overlay[]> {
  const { data } = await apiClient.get<Overlay[]>('/overlays');
  return data;
}

export async function createOverlay(overlay: CreateOverlayDto): Promise<Overlay> {
  const { data } = await apiClient.post<Overlay>('/overlays', overlay);
  return data;
}

export async function updateOverlay(id: string, updates: UpdateOverlayDto): Promise<Overlay> {
  const { data } = await apiClient.put<Overlay>(`/overlays/${id}`, updates);
  return data;
}

export async function deleteOverlay(id: string): Promise<string> {
  await apiClient.delete(`/overlays/${id}`);
  return id;
}
