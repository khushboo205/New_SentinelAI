import React, { useState, useRef, useEffect, useCallback } from 'react';
import {
  Columns,
  SplitSquareVertical,
  Zap,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Maximize2,
  Minimize2,
  Sliders,
  Move,
} from 'lucide-react';

interface ComparisonSliderProps {
  originalSrc: string;
  enhancedSrc: string;
  originalLabel?: string;
  enhancedLabel?: string;
  originalHash?: string;
  enhancedHash?: string;
  className?: string;
  onSelectCrop?: (cropRect: { x: number; y: number; width: number; height: number }) => void;
}

export const ComparisonSlider: React.FC<ComparisonSliderProps> = ({
  originalSrc,
  enhancedSrc,
  originalLabel = 'ORIGINAL CAPTURE',
  enhancedLabel = 'ENHANCED DERIVATIVE',
  originalHash,
  enhancedHash,
  className = '',
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [sliderPos, setSliderPos] = useState<number>(50); // 0 to 100
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [viewMode, setViewMode] = useState<'split' | 'side-by-side' | 'blink'>('split');
  const [blinkState, setBlinkState] = useState<'original' | 'enhanced'>('enhanced');
  const [zoomLevel, setZoomLevel] = useState<number>(1); // 1 to 4
  const [pan, setPan] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState<boolean>(false);
  const panStartRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);
  const [showToneControls, setShowToneControls] = useState<boolean>(false);
  const [exposure, setExposure] = useState<number>(100); // 50 to 200%
  const [contrast, setContrast] = useState<number>(100); // 50 to 200%

  // Blink comparator interval
  useEffect(() => {
    if (viewMode !== 'blink') return;
    const interval = setInterval(() => {
      setBlinkState((prev) => (prev === 'original' ? 'enhanced' : 'original'));
    }, 600);
    return () => clearInterval(interval);
  }, [viewMode]);

  // Handle slider drag
  const handlePointerMove = useCallback(
    (e: PointerEvent) => {
      if (!isDragging || !containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const clientX = e.clientX;
      const x = Math.max(0, Math.min(clientX - rect.left, rect.width));
      const percentage = (x / rect.width) * 100;
      setSliderPos(percentage);
    },
    [isDragging]
  );

  const handlePointerUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  useEffect(() => {
    if (isDragging) {
      window.addEventListener('pointermove', handlePointerMove);
      window.addEventListener('pointerup', handlePointerUp);
    }
    return () => {
      window.removeEventListener('pointermove', handlePointerMove);
      window.removeEventListener('pointerup', handlePointerUp);
    };
  }, [isDragging, handlePointerMove, handlePointerUp]);

  // Handle Pan when zoomed in
  const handleMouseDown = (e: React.MouseEvent) => {
    if (zoomLevel > 1 && e.button === 0 && !isDragging) {
      setIsPanning(true);
      panStartRef.current = { x: e.clientX - pan.x, y: e.clientY - pan.y };
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isPanning && zoomLevel > 1) {
      setPan({
        x: e.clientX - panStartRef.current.x,
        y: e.clientY - panStartRef.current.y,
      });
    }
  };

  const handleMouseUp = () => {
    setIsPanning(false);
  };

  const handleZoom = (delta: number) => {
    setZoomLevel((prev) => {
      const next = Math.max(1, Math.min(prev + delta, 4));
      if (next === 1) setPan({ x: 0, y: 0 });
      return next;
    });
  };

  const handleReset = () => {
    setZoomLevel(1);
    setPan({ x: 0, y: 0 });
    setSliderPos(50);
    setExposure(100);
    setContrast(100);
  };

  const toggleFullscreen = () => {
    if (!containerRef.current) return;
    if (!document.fullscreenElement) {
      containerRef.current.requestFullscreen?.().catch(() => {});
      setIsFullscreen(true);
    } else {
      document.exitFullscreen?.().catch(() => {});
      setIsFullscreen(false);
    }
  };

  const imageFilterStyle = {
    filter: `brightness(${exposure}%) contrast(${contrast}%)`,
  };

  return (
    <div
      ref={containerRef}
      className={`relative flex flex-col bg-[#07090e] border border-[#222b3a] rounded select-none overflow-hidden ${className}`}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
    >
      {/* Top Controls Toolbar */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-[#161c26] bg-[#0b0e14] text-xs z-20">
        <div className="flex items-center gap-1">
          <button
            onClick={() => setViewMode('split')}
            className={`wb-btn ${viewMode === 'split' ? 'wb-btn-primary' : 'wb-btn-ghost'}`}
            title="Split-screen slider comparison (Drag center bar)"
          >
            <SplitSquareVertical className="w-3.5 h-3.5" />
            <span>Split</span>
          </button>
          <button
            onClick={() => setViewMode('side-by-side')}
            className={`wb-btn ${viewMode === 'side-by-side' ? 'wb-btn-primary' : 'wb-btn-ghost'}`}
            title="Side-by-side adjacent comparison"
          >
            <Columns className="w-3.5 h-3.5" />
            <span>Side by Side</span>
          </button>
          <button
            onClick={() => setViewMode('blink')}
            className={`wb-btn ${viewMode === 'blink' ? 'wb-btn-primary' : 'wb-btn-ghost'}`}
            title="Forensic blink comparator (alternates between Original and Enhanced)"
          >
            <Zap className="w-3.5 h-3.5" />
            <span>Blink</span>
          </button>
        </div>

        {/* Zoom, Tone & Pan Controls */}
        <div className="flex items-center gap-2">
          {/* Tone Filter Toggle */}
          <button
            onClick={() => setShowToneControls(!showToneControls)}
            className={`wb-btn ${showToneControls ? 'wb-btn-primary' : 'wb-btn-ghost'} py-1 px-2 text-[11px]`}
            title="Toggle client-side exposure & contrast tone curves"
          >
            <Sliders className="w-3.5 h-3.5" />
            <span>Tone Controls</span>
          </button>

          {/* Zoom Controls */}
          <div className="flex items-center gap-0.5 bg-[#10141a] border border-[#222b3a] rounded px-1 py-0.5">
            <button
              onClick={() => handleZoom(-0.5)}
              disabled={zoomLevel <= 1}
              className="p-1 hover:text-[#e6edf3] text-[#94a3b8] disabled:opacity-30 cursor-pointer"
              title="Zoom out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <span className="font-mono text-[11px] px-1.5 text-[#cbd5e1]">
              {Math.round(zoomLevel * 100)}%
            </span>
            <button
              onClick={() => handleZoom(0.5)}
              disabled={zoomLevel >= 4}
              className="p-1 hover:text-[#e6edf3] text-[#94a3b8] disabled:opacity-30 cursor-pointer"
              title="Zoom in"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
          </div>

          <button
            onClick={handleReset}
            className="wb-btn wb-btn-ghost p-1.5"
            title="Reset zoom, pan, & slider position"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>

          <button
            onClick={toggleFullscreen}
            className="wb-btn wb-btn-ghost p-1.5"
            title="Toggle fullscreen inspect"
          >
            {isFullscreen ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* Tone Curves Sub-Bar (When Toggled) */}
      {showToneControls && (
        <div className="flex items-center gap-6 px-4 py-1.5 bg-[#0e1218] border-b border-[#161c26] text-xs font-mono text-[#cbd5e1] z-20">
          <div className="flex items-center gap-2 flex-1">
            <span className="text-[10px] text-[#64748b] font-sans">EXPOSURE:</span>
            <input
              type="range"
              min="50"
              max="180"
              value={exposure}
              onChange={(e) => setExposure(Number(e.target.value))}
              className="wb-slider flex-1"
            />
            <span className="w-10 text-right">{exposure}%</span>
          </div>

          <div className="flex items-center gap-2 flex-1">
            <span className="text-[10px] text-[#64748b] font-sans">CONTRAST:</span>
            <input
              type="range"
              min="60"
              max="160"
              value={contrast}
              onChange={(e) => setContrast(Number(e.target.value))}
              className="wb-slider flex-1"
            />
            <span className="w-10 text-right">{contrast}%</span>
          </div>

          <button
            onClick={() => {
              setExposure(100);
              setContrast(100);
            }}
            className="text-[10px] text-[#f59e0b] hover:underline"
          >
            Reset Tone
          </button>
        </div>
      )}

      {/* Main Image Comparison Canvas */}
      <div
        className={`relative flex-1 min-h-[380px] bg-[#07090e] overflow-hidden flex items-center justify-center ${
          zoomLevel > 1 ? (isPanning ? 'cursor-grabbing' : 'cursor-grab') : 'cursor-crosshair'
        }`}
      >
        {/* MODE 1: SPLIT SCREEN SLIDER */}
        {viewMode === 'split' && (
          <div
            className="relative w-full h-full flex items-center justify-center overflow-hidden"
            style={{
              transform: `scale(${zoomLevel}) translate(${pan.x / zoomLevel}px, ${pan.y / zoomLevel}px)`,
              transformOrigin: 'center center',
            }}
          >
            {/* Enhanced Image (Base background layer) */}
            <img
              src={enhancedSrc}
              alt={enhancedLabel}
              style={imageFilterStyle}
              className="absolute inset-0 w-full h-full object-contain pointer-events-none select-none"
            />

            {/* Original Image (Clipped overlay layer) */}
            <div
              className="absolute inset-0 w-full h-full overflow-hidden pointer-events-none select-none"
              style={{ clipPath: `inset(0 ${100 - sliderPos}% 0 0)` }}
            >
              <img
                src={originalSrc}
                alt={originalLabel}
                style={imageFilterStyle}
                className="absolute inset-0 w-full h-full object-contain select-none"
              />
            </div>

            {/* Draggable Divider Line */}
            <div
              className="absolute top-0 bottom-0 w-[2px] bg-[#d97706] cursor-ew-resize z-10"
              style={{ left: `${sliderPos}%` }}
              onPointerDown={(e) => {
                e.preventDefault();
                setIsDragging(true);
              }}
            >
              <div className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-6 h-6 rounded-full bg-[#10141a] border-2 border-[#f59e0b] flex items-center justify-center shadow-lg text-[10px] text-[#f59e0b]">
                ⇄
              </div>
            </div>

            {/* Left/Right Overlaid Identification Labels */}
            <div className="absolute bottom-3 left-3 bg-[#0b0e14]/90 border border-[#222b3a] px-2 py-1 rounded text-[11px] pointer-events-none z-10 flex flex-col gap-0.5">
              <span className="text-[#94a3b8] font-sans font-medium uppercase tracking-wider">{originalLabel}</span>
              {originalHash && <span className="text-[10px] font-mono text-[#64748b]">SHA: {originalHash.slice(0, 8)}...</span>}
            </div>
            <div className="absolute bottom-3 right-3 bg-[#0b0e14]/90 border border-[#222b3a] px-2 py-1 rounded text-[11px] pointer-events-none z-10 flex flex-col items-end gap-0.5">
              <span className="text-[#f59e0b] font-sans font-medium uppercase tracking-wider">{enhancedLabel}</span>
              {enhancedHash && <span className="text-[10px] font-mono text-[#64748b]">SHA: {enhancedHash.slice(0, 8)}...</span>}
            </div>
          </div>
        )}

        {/* MODE 2: SIDE BY SIDE */}
        {viewMode === 'side-by-side' && (
          <div
            className="grid grid-cols-2 w-full h-full divide-x divide-[#222b3a]"
            style={{
              transform: `scale(${zoomLevel}) translate(${pan.x / zoomLevel}px, ${pan.y / zoomLevel}px)`,
              transformOrigin: 'center center',
            }}
          >
            {/* Left: Original */}
            <div className="relative flex flex-col items-center justify-center p-2 bg-[#07090e]">
              <img
                src={originalSrc}
                alt={originalLabel}
                style={imageFilterStyle}
                className="w-full h-full object-contain select-none"
              />
              <div className="absolute top-3 left-3 bg-[#0b0e14]/90 border border-[#222b3a] px-2 py-0.5 rounded text-[10px] text-[#94a3b8] uppercase tracking-wider">
                {originalLabel}
              </div>
            </div>

            {/* Right: Enhanced */}
            <div className="relative flex flex-col items-center justify-center p-2 bg-[#07090e]">
              <img
                src={enhancedSrc}
                alt={enhancedLabel}
                style={imageFilterStyle}
                className="w-full h-full object-contain select-none"
              />
              <div className="absolute top-3 right-3 bg-[#0b0e14]/90 border border-[#222b3a] px-2 py-0.5 rounded text-[10px] text-[#f59e0b] uppercase tracking-wider">
                {enhancedLabel}
              </div>
            </div>
          </div>
        )}

        {/* MODE 3: RAPID BLINK COMPARATOR */}
        {viewMode === 'blink' && (
          <div
            className="relative w-full h-full flex items-center justify-center"
            style={{
              transform: `scale(${zoomLevel}) translate(${pan.x / zoomLevel}px, ${pan.y / zoomLevel}px)`,
              transformOrigin: 'center center',
            }}
          >
            <img
              src={blinkState === 'original' ? originalSrc : enhancedSrc}
              alt="Blink view"
              style={imageFilterStyle}
              className="w-full h-full object-contain select-none"
            />
            <div className="absolute top-3 left-3 flex items-center gap-2 bg-[#0b0e14]/90 border border-[#222b3a] px-2.5 py-1 rounded text-xs">
              <span className="w-2 h-2 rounded-full animate-ping bg-[#f59e0b]" />
              <span className="font-mono uppercase font-semibold text-[#f59e0b]">
                {blinkState === 'original' ? originalLabel : enhancedLabel}
              </span>
            </div>
          </div>
        )}

        {/* MINIMAP NAVIGATOR FOR DEEP ZOOM */}
        {zoomLevel > 1 && (
          <div className="absolute bottom-4 right-4 w-28 h-20 bg-[#0b0e14]/90 border border-[#222b3a] rounded p-1 shadow-2xl z-20 pointer-events-none flex flex-col justify-between">
            <div className="relative flex-1 bg-black rounded overflow-hidden">
              <img
                src={enhancedSrc}
                alt="Minimap"
                className="w-full h-full object-cover opacity-60"
              />
              {/* Active Viewport Rectangle */}
              <div
                className="absolute border-2 border-[#f59e0b] bg-[#f59e0b]/20"
                style={{
                  width: `${Math.max(20, 100 / zoomLevel)}%`,
                  height: `${Math.max(20, 100 / zoomLevel)}%`,
                  top: `${Math.max(0, Math.min(80, 50 - (pan.y / (zoomLevel * 3))))}%`,
                  left: `${Math.max(0, Math.min(80, 50 - (pan.x / (zoomLevel * 3))))}%`,
                }}
              />
            </div>
            <div className="text-[9px] font-mono text-[#64748b] flex justify-between px-0.5 mt-0.5">
              <span>{Math.round(zoomLevel * 100)}%</span>
              <span>PAN ACTIVE</span>
            </div>
          </div>
        )}
      </div>

      {/* Bottom Range Slider Scrub Bar */}
      {viewMode === 'split' && (
        <div className="flex items-center gap-3 px-3 py-1.5 border-t border-[#161c26] bg-[#0b0e14]">
          <span className="text-[10px] text-[#64748b] font-mono">0% (RAW)</span>
          <input
            type="range"
            min="0"
            max="100"
            value={sliderPos}
            onChange={(e) => setSliderPos(Number(e.target.value))}
            className="wb-slider flex-1"
            aria-label="Comparison slider position"
          />
          <span className="text-[10px] text-[#64748b] font-mono">100% (ENHANCED)</span>
        </div>
      )}
    </div>
  );
};
