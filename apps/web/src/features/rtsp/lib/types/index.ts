export interface RtspConnectRequest {
  rtsp_url: string;
}

export interface RtspConnectResponse {
  status: string;
  url: string;
  streamPath: string;
  streamUrl: string;
}

export interface RtspStatusResponse {
  status: 'live' | 'idle';
  url: string | null;
}
