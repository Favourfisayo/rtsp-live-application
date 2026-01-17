import { useState, useRef } from 'react';
import type { Route } from './+types/_index';

import { VideoPlayer, RtspInput } from '../features/rtsp';
import {
  OverlayBox,
  OverlayControls,
  useOverlays,
  useCreateOverlay,
  useUpdateOverlay,
  useDeleteOverlay,
  type Overlay,
  type CreateOverlayDto,
} from '../features/overlays';

export function meta({}: Route.MetaArgs) {
  return [
    { title: 'RTSP Live Overlay' },
    { name: 'description', content: 'Play RTSP streams and add overlays' },
  ];
}

export default function Index() {
  const [streamUrl, setStreamUrl] = useState<string | null>(null);
  const [selectedOverlayId, setSelectedOverlayId] = useState<string | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const { data: overlays = [] } = useOverlays();
  const createMutation = useCreateOverlay();
  const updateMutation = useUpdateOverlay();
  const deleteMutation = useDeleteOverlay(() => setSelectedOverlayId(null));

  const handleCreate = (dto: CreateOverlayDto) => {
    const rect = containerRef.current?.getBoundingClientRect();
    const x = rect ? rect.width / 2 - dto.width / 2 : 50;
    const y = rect ? rect.height / 2 - dto.height / 2 : 50;
    createMutation.mutate({ ...dto, x, y });
  };

  const handleUpdate = (id: string, updates: Partial<Overlay>) => {
    updateMutation.mutate({ id, updates });
  };

  const handleDelete = (id: string) => {
    if (confirm('Are you sure you want to delete this overlay?')) {
      deleteMutation.mutate(id);
    }
  };

  return (
    <div className="flex flex-1 h-full overflow-hidden">
      <div className="flex-1 flex flex-col bg-neutral-900 relative">
        <div
          className="flex-1 relative overflow-hidden flex items-center justify-center p-4"
          ref={containerRef}
        >
          {streamUrl ? (
            <div className="relative w-full h-full flex items-center justify-center">
              <VideoPlayer src={streamUrl} className="w-full h-full" />

              <div className="absolute inset-0 z-10 overflow-hidden pointer-events-none">
                {overlays.map((overlay) => (
                  <OverlayBox
                    key={overlay._id}
                    overlay={overlay}
                    isSelected={selectedOverlayId === overlay._id}
                    onSelect={setSelectedOverlayId}
                    onUpdate={handleUpdate}
                  />
                ))}
              </div>
            </div>
          ) : (
            <div className="w-full h-full flex items-center justify-center flex-col gap-4">
              <div className="text-center space-y-2">
                <h1 className="text-2xl font-bold text-white">RTSP Live Overlay</h1>
                <p className="text-muted-foreground">Enter an RTSP URL to begin</p>
              </div>
              <RtspInput onStreamStart={setStreamUrl} />
            </div>
          )}
        </div>
      </div>

      <OverlayControls
        overlays={overlays}
        selectedId={selectedOverlayId}
        onSelect={setSelectedOverlayId}
        onCreate={handleCreate}
        onUpdate={handleUpdate}
        onDelete={handleDelete}
        isCreating={createMutation.isPending}
      />
    </div>
  );
}
