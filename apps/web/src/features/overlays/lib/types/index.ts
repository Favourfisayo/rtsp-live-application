export type OverlayType = 'text' | 'image';

export interface Overlay {
  _id: string;
  type: OverlayType;
  content: string;
  imageUrl?: string;
  x: number;
  y: number;
  width: number;
  height: number;
  zIndex?: number;
  visible?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface CreateOverlayDto {
  type: OverlayType;
  content: string;
  imageUrl?: string;
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface UpdateOverlayDto {
  type?: OverlayType;
  content?: string;
  imageUrl?: string;
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  zIndex?: number;
  visible?: boolean;
}

export interface OverlayPosition {
  x: number;
  y: number;
}

export interface OverlaySize {
  width: number;
  height: number;
}
