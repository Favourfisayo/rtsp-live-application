import { useState, useEffect, type ChangeEvent, type MouseEvent, Activity } from 'react';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import { Label } from '../../../components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/card';
import { Plus, Trash2, Type, Image as ImageIcon, Save } from 'lucide-react';
import type { Overlay, CreateOverlayDto, OverlayType } from '../lib/types';

interface OverlayControlsProps {
  overlays: Overlay[];
  selectedId: string | null;
  onSelect: (id: string | null) => void;
  onCreate: (overlay: CreateOverlayDto) => void;
  onUpdate: (id: string, updates: Partial<Overlay>) => void;
  onDelete: (id: string) => void;
  isCreating: boolean;
}

const DEFAULT_OVERLAY_DIMENSIONS = {
  width: 200,
  height: 100,
  x: 50,
  y: 50,
} as const;

export function OverlayControls({
  overlays,
  selectedId,
  onSelect,
  onCreate,
  onUpdate,
  onDelete,
  isCreating,
}: OverlayControlsProps) {
  const [newType, setNewType] = useState<OverlayType>('text');
  const [newContent, setNewContent] = useState('');
  const [editContent, setEditContent] = useState('');
  const [editImageUrl, setEditImageUrl] = useState('');

  const selectedOverlay = overlays.find((o) => o._id === selectedId);

  useEffect(() => {
    if (selectedOverlay) {
      setEditContent(selectedOverlay.content);
      setEditImageUrl(selectedOverlay.imageUrl || '');
    }
  }, [selectedOverlay?._id, selectedOverlay?.content, selectedOverlay?.imageUrl]);

  const handleCreate = () => {
    if (!newContent) return;

    onCreate({
      type: newType,
      content: newContent,
      ...DEFAULT_OVERLAY_DIMENSIONS,
    });
    setNewContent('');
  };

  const handleSaveEdit = () => {
    if (!selectedOverlay) return;
    
    if (selectedOverlay.type === 'image') {
      if (editImageUrl !== selectedOverlay.imageUrl) {
        onUpdate(selectedOverlay._id, { imageUrl: editImageUrl });
      }
    } else {
      if (editContent !== selectedOverlay.content) {
        onUpdate(selectedOverlay._id, { content: editContent });
      }
    }
  };

  const handleDeleteClick = (e: MouseEvent<HTMLButtonElement>, id: string) => {
    e.stopPropagation();
    onDelete(id);
  };

  return (
    <div className="h-full flex flex-col gap-4 p-4 border-l bg-neutral-50 dark:bg-neutral-900 w-90 overflow-y-auto">
      <div className="space-y-4">
        <h2 className="text-lg font-semibold tracking-tight">Overlays</h2>

        <Card>
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-sm font-medium">Add Overlay</CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-0 gap-3 flex flex-col">
            <div className="flex gap-2">
              <Button
                variant={newType === 'text' ? 'default' : 'outline'}
                size="sm"
                className="flex-1"
                onClick={() => setNewType('text')}
              >
                <Type className="h-4 w-4 mr-2" /> Text
              </Button>
              <Button
                variant={newType === 'image' ? 'default' : 'outline'}
                size="sm"
                className="flex-1"
                onClick={() => setNewType('image')}
              >
                <ImageIcon className="h-4 w-4 mr-2" /> Image
              </Button>
            </div>

            <div className="space-y-1">
              <Label htmlFor="new-content" className="text-xs">
                {newType === 'text' ? 'Content' : 'Image URL'}
              </Label>
              <Input
                id="new-content"
                value={newContent}
                onChange={(e: ChangeEvent<HTMLInputElement>) => setNewContent(e.target.value)}
                placeholder={newType === 'text' ? 'Enter text...' : 'https://...'}
                className="h-8"
              />
            </div>

            <Button
              onClick={handleCreate}
              disabled={isCreating || !newContent}
              className="w-full"
            >
              <Plus className="h-4 w-4 mr-2" />
              {isCreating ? 'Adding...' : 'Add to Stream'}
            </Button>
          </CardContent>
        </Card>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto space-y-3 pr-1">
        <h3 className="text-sm font-medium text-muted-foreground sticky top-0 bg-neutral-50 dark:bg-neutral-900 py-1">Layers</h3>
        
        <Activity mode={overlays.length === 0 ? 'visible' : 'hidden'}>
          <div className="text-center p-8 border-2 border-dashed rounded-lg text-muted-foreground text-sm">
            No overlays yet. Add one above!
          </div>
        </Activity>

        {overlays.map((overlay) => (
          <div
            key={overlay._id}
            className={`p-3 rounded-md border text-sm cursor-pointer transition-colors flex items-center justify-between group ${
              selectedId === overlay._id
                ? 'bg-accent text-accent-foreground border-primary'
                : 'bg-card hover:bg-accent/50'
            }`}
            onClick={() => onSelect(overlay._id)}
          >
            <div className="flex items-center gap-3 truncate">
              {overlay.type === 'text' ? (
                <Type className="h-4 w-4 text-muted-foreground" />
              ) : (
                <ImageIcon className="h-4 w-4 text-muted-foreground" />
              )}
              <span className="truncate font-medium">
                {overlay.type === 'image' ? overlay.imageUrl : overlay.content}
              </span>
            </div>
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6 shrink-0 text-destructive hover:text-destructive hover:bg-destructive/10"
              onClick={(e) => handleDeleteClick(e, overlay._id)}
            >
              <Trash2 className="h-3 w-3" />
            </Button>
          </div>
        ))}
      </div>

      <Activity mode={selectedOverlay ? 'visible' : 'hidden'}>
        <Card className="shrink-0 animate-in slide-in-from-bottom-5 border-primary/20">
          <CardHeader className="p-4 pb-2 bg-muted/30">
            <CardTitle className="text-sm font-medium flex items-center justify-between">
              Edit Layer
              <span className="text-xs font-normal text-muted-foreground font-mono">
                {selectedOverlay?.width}x{selectedOverlay?.height}
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 space-y-3">
            <div className="space-y-1">
              <Label htmlFor="content">
                {selectedOverlay?.type === 'image' ? 'Image URL' : 'Content'}
              </Label>
              {selectedOverlay?.type === 'image' ? (
                <Input
                  id="content"
                  value={editImageUrl}
                  onChange={(e: ChangeEvent<HTMLInputElement>) => setEditImageUrl(e.target.value)}
                  placeholder="https://..."
                />
              ) : (
                <Input
                  id="content"
                  value={editContent}
                  onChange={(e: ChangeEvent<HTMLInputElement>) => setEditContent(e.target.value)}
                />
              )}
            </div>

            <Button
              onClick={handleSaveEdit}
              disabled={
                selectedOverlay?.type === 'image'
                  ? editImageUrl === selectedOverlay?.imageUrl
                  : editContent === selectedOverlay?.content
              }
              className="w-full"
              size="sm"
            >
              <Save className="h-4 w-4 mr-2" />
              Save Changes
            </Button>

            <Button
              variant="destructive"
              onClick={() => selectedOverlay && onDelete(selectedOverlay._id)}
              className="w-full"
              size="sm"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Delete Overlay
            </Button>

            <Activity mode={selectedOverlay?.type === 'text' ? 'visible' : 'hidden'}>
              <div className="text-xs text-muted-foreground">
                Tip: Drag corners to resize font.
              </div>
            </Activity>
          </CardContent>
        </Card>
      </Activity>
    </div>
  );
}
