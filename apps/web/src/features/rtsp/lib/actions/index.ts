/**
 * RTSP API actions - handles all RTSP stream-related API calls.
 */

import { apiClient } from '../../../../lib/api-client';
import type { RtspConnectResponse, RtspStatusResponse } from '../types';

const STREAM_CONNECT_TIMEOUT = 60000;

export async function connectStream(rtspUrl: string): Promise<RtspConnectResponse> {
  const { data } = await apiClient.post<RtspConnectResponse>(
    '/rtsp/connect',
    { rtsp_url: rtspUrl },
    { timeout: STREAM_CONNECT_TIMEOUT }
  );
  return data;
}

export async function disconnectStream(): Promise<void> {
  await apiClient.post('/rtsp/disconnect');
}

export async function getStreamStatus(): Promise<RtspStatusResponse> {
  const { data } = await apiClient.get<RtspStatusResponse>('/rtsp/status');
  return data;
}
