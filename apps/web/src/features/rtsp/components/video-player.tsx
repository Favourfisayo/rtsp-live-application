import { useEffect, useRef, useState, useCallback, Activity } from 'react';
import Hls from 'hls.js';
import { cn } from '../../../lib/utils';
import { Play, Pause, Volume2, VolumeX, RefreshCw } from 'lucide-react';
import { Button } from '../../../components/ui/button';

interface VideoPlayerProps {
  src: string | null;
  className?: string;
  onError?: (error: string) => void;
}

interface PlayerState {
  isPlaying: boolean;
  isMuted: boolean;
  isLoading: boolean;
  hasError: boolean;
}

const INITIAL_PLAYER_STATE: PlayerState = {
  isPlaying: false,
  isMuted: true,
  isLoading: false,
  hasError: false,
};

const HLS_CONFIG = {
  enableWorker: true,
  lowLatencyMode: false,
  backBufferLength: 60,
  maxBufferLength: 30,
  maxMaxBufferLength: 60,
  maxBufferSize: 30 * 1024 * 1024,
  maxBufferHole: 0.5,
  liveSyncDurationCount: 3,
  liveMaxLatencyDurationCount: 6,
  liveDurationInfinity: true,
  manifestLoadingTimeOut: 20000,
  manifestLoadingMaxRetry: 10,
  manifestLoadingRetryDelay: 500,
  levelLoadingTimeOut: 20000,
  levelLoadingMaxRetry: 10,
  levelLoadingRetryDelay: 500,
  fragLoadingTimeOut: 30000,
  fragLoadingMaxRetry: 10,
  fragLoadingRetryDelay: 500,
  nudgeOffset: 0.1,
  nudgeMaxRetry: 5,
  maxFragLookUpTolerance: 0.25,
  startPosition: -1,
} as const;

export function VideoPlayer({ src, className, onError }: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const hlsRef = useRef<Hls | null>(null);
  const [state, setState] = useState<PlayerState>(INITIAL_PLAYER_STATE);

  const updateState = useCallback((updates: Partial<PlayerState>) => {
    setState((prev) => ({ ...prev, ...updates }));
  }, []);

  const destroyHls = useCallback(() => {
    if (hlsRef.current) {
      hlsRef.current.destroy();
      hlsRef.current = null;
    }
  }, []);

  const initHls = useCallback(() => {
    const video = videoRef.current;
    if (!video || !src) return;

    destroyHls();
    updateState({ isLoading: true, hasError: false });

    if (Hls.isSupported() && src.endsWith('.m3u8')) {
      const hls = new Hls(HLS_CONFIG);
      hlsRef.current = hls;
      
      hls.loadSource(src);
      hls.attachMedia(video);

      hls.on(Hls.Events.MANIFEST_PARSED, () => {
        updateState({ isLoading: false, isPlaying: true });
        video.play().catch(() => updateState({ isPlaying: false }));
      });

      hls.on(Hls.Events.ERROR, (_, data) => {
        if (!data.fatal) return;
        
        updateState({ isLoading: false });
        
        switch (data.type) {
          case Hls.ErrorTypes.NETWORK_ERROR:
            hls.startLoad();
            break;
          case Hls.ErrorTypes.MEDIA_ERROR:
            hls.recoverMediaError();
            break;
          default:
            updateState({ hasError: true });
            onError?.(`HLS Error: ${data.details}`);
            hls.destroy();
        }
      });
      return;
    }
    
    video.src = src;
    video.play().catch(() => updateState({ isPlaying: false }));
  }, [src, onError, destroyHls, updateState]);

  useEffect(() => {
    initHls();
    return destroyHls;
  }, [initHls, destroyHls]);

  const togglePlay = () => {
    const video = videoRef.current;
    if (!video) return;
    
    if (state.isPlaying) {
      video.pause();
    } else {
      video.play();
    }
    updateState({ isPlaying: !state.isPlaying });
  };

  const toggleMute = () => {
    const video = videoRef.current;
    if (!video) return;
    
    video.muted = !state.isMuted;
    updateState({ isMuted: !state.isMuted });
  };

  return (
    <div className={cn('relative bg-black rounded-lg overflow-hidden group', className)}>
      <video
        ref={videoRef}
        className="w-full h-full object-contain"
        muted={state.isMuted}
        playsInline
        onPlay={() => updateState({ isPlaying: true })}
        onPause={() => updateState({ isPlaying: false })}
        onWaiting={() => updateState({ isLoading: true })}
        onPlaying={() => updateState({ isLoading: false })}
      />

      <Activity mode={state.isLoading && src ? 'visible' : 'hidden'}>
        <div className="absolute inset-0 flex items-center justify-center bg-black/50">
          <div className="flex flex-col items-center gap-2">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-white" />
            <p className="text-white text-sm">Loading stream...</p>
          </div>
        </div>
      </Activity>

      <Activity mode={state.hasError ? 'visible' : 'hidden'}>
        <div className="absolute inset-0 flex items-center justify-center bg-black/70">
          <div className="flex flex-col items-center gap-4">
            <p className="text-white text-sm">Failed to load stream</p>
            <Button
              variant="outline"
              size="sm"
              onClick={initHls}
              className="text-white border-white hover:bg-white/20"
            >
              <RefreshCw className="mr-2 h-4 w-4" />
              Retry
            </Button>
          </div>
        </div>
      </Activity>

      <div className="absolute bottom-0 left-0 right-0 p-4 bg-linear-to-t from-black/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={togglePlay}
            className="text-white hover:bg-white/20"
          >
            {state.isPlaying ? <Pause className="h-6 w-6" /> : <Play className="h-6 w-6" />}
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleMute}
            className="text-white hover:bg-white/20"
          >
            {state.isMuted ? <VolumeX className="h-6 w-6" /> : <Volume2 className="h-6 w-6" />}
          </Button>
        </div>
      </div>

      <Activity mode={!src ? 'visible' : 'hidden'}>
        <div className="absolute inset-0 flex items-center justify-center text-white/50">
          <p>No stream source</p>
        </div>
      </Activity>
    </div>
  );
}
