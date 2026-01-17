import { useState, useEffect, useRef, Activity } from 'react';
import { Rnd, type RndResizeCallback, type RndDragCallback } from 'react-rnd';
import { cn } from '../../../lib/utils';
import type { Overlay, OverlayPosition, OverlaySize } from '../lib/types';

interface OverlayBoxProps {
  overlay: Overlay;
  isSelected: boolean;
  onSelect: (id: string) => void;
  onUpdate: (id: string, updates: Partial<Overlay>) => void;
}

// Debounce delay in milliseconds
const DEBOUNCE_DELAY = 500;

export function OverlayBox({
  overlay,
  isSelected,
  onSelect,
  onUpdate
}: OverlayBoxProps) {
  const [position, setPosition] = useState<OverlayPosition>({ x: overlay.x, y: overlay.y });
  const [size, setSize] = useState<OverlaySize>({ width: overlay.width, height: overlay.height });
  const [imageError, setImageError] = useState(false);
  const updateTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    setPosition({ x: overlay.x, y: overlay.y });
    setSize({ width: overlay.width, height: overlay.height });
  }, [overlay.x, overlay.y, overlay.width, overlay.height]);

  useEffect(() => {
    setImageError(false);
  }, [overlay.content]);

  
  useEffect(() => {
    return () => {
      if (updateTimeoutRef.current) {
        clearTimeout(updateTimeoutRef.current);
      }
    };
  }, []);

  const debouncedUpdate = (updates: Partial<Overlay>) => {

    if (updateTimeoutRef.current) {
      clearTimeout(updateTimeoutRef.current);
    }


    updateTimeoutRef.current = setTimeout(() => {
      onUpdate(overlay._id, updates);
      updateTimeoutRef.current = null;
    }, DEBOUNCE_DELAY);
  };

  const handleDragStop: RndDragCallback = (_, d) => {
    const newPosition = { x: d.x, y: d.y };
    setPosition(newPosition);
    debouncedUpdate(newPosition);
  };

  const handleResizeStop: RndResizeCallback = (_, __, ref, ___, pos) => {
    const newSize = {
      width: parseInt(ref.style.width),
      height: parseInt(ref.style.height),
    };
    setSize(newSize);
    setPosition(pos);
    debouncedUpdate({ ...newSize, x: pos.x, y: pos.y });
  };

  return (
    <Rnd
      size={size}
      position={position}
      onDragStop={handleDragStop}
      onResizeStop={handleResizeStop}
      onMouseDown={() => onSelect(overlay._id)}
      bounds="parent"
      className={cn(
        'absolute cursor-move border-2 transition-colors pointer-events-auto',
        isSelected
          ? 'border-primary z-50'
          : 'border-transparent hover:border-primary/50 z-10'
      )}
      resizeHandleStyles={{
        bottomRight: { cursor: 'se-resize' },
        bottomLeft: { cursor: 'sw-resize' },
        topRight: { cursor: 'ne-resize' },
        topLeft: { cursor: 'nw-resize' },
      }}
    >
      <div className={cn(
        'w-full h-full relative overflow-hidden flex items-center justify-center backdrop-blur-sm',
        imageError ? 'bg-red-500/50' : 'bg-black/20'
      )}>
        {overlay.type === 'text' ? (
          <p
            className="text-white font-bold select-none p-2 text-center"
            style={{ fontSize: 'clamp(12px, 2cqw, 24px)' }}
          >
            {overlay.content}
          </p>
        ) : (
          <Activity mode={imageError ? 'hidden' : 'visible'}>
            <img
              src={overlay.content}
              alt="Overlay"
              className="w-full h-full object-contain pointer-events-none select-none"
              onError={() => setImageError(true)}
            />
          </Activity>
        )}
        
        <Activity mode={isSelected ? 'visible' : 'hidden'}>
          <div className="absolute top-0 right-0 p-1 bg-primary text-primary-foreground text-xs font-mono">
            {Math.round(position.x)}, {Math.round(position.y)}
          </div>
        </Activity>
      </div>
    </Rnd>
  );
}
