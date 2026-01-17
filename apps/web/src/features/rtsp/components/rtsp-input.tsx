import { useState, type FormEvent } from 'react';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import { PlayCircle, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { connectStream } from '../lib/actions';
import { handleApiError } from '../../../lib/errors';

interface RtspInputProps {
  onStreamStart: (streamUrl: string) => void;
}

const RTSP_PROTOCOL_PREFIX = 'rtsp://';

function isValidRtspUrl(url: string): boolean {
  return url.startsWith(RTSP_PROTOCOL_PREFIX);
}

export function RtspInput({ onStreamStart }: RtspInputProps) {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (!url) return;

    if (!isValidRtspUrl(url)) {
      toast.error('Invalid URL', { description: 'URL must start with rtsp://' });
      return;
    }

    setIsLoading(true);
    
    try {
      const response = await connectStream(url);
      onStreamStart(response.streamUrl);
      toast.success('Stream started successfully');
    } catch (error) {
      handleApiError(error, 'Stream connection');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form 
      onSubmit={handleSubmit} 
      className="flex gap-2 w-full max-w-2xl mx-auto p-4 bg-card rounded-lg border shadow-sm"
    >
      <Input
        placeholder="Enter RTSP URL (rtsp://...)"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        className="flex-1 font-mono text-sm"
        disabled={isLoading}
      />
      <Button type="submit" disabled={isLoading || !url}>
        {isLoading ? (
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
        ) : (
          <PlayCircle className="mr-2 h-4 w-4" />
        )}
        Play Stream
      </Button>
    </form>
  );
}
