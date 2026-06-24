import { useRef, type PointerEvent } from "react";
import { MapPin } from "lucide-react";

/**
 * Kenya bounding-box picker. Click/drag on the canvas to set GPS coords.
 * Bounds: lat -5 → 5, lng 33.5 → 42.
 */
export const KENYA_BOUNDS = {
  minLat: -5,
  maxLat: 5,
  minLng: 33.5,
  maxLng: 42,
} as const;

export function isInKenya(lat: number, lng: number) {
  return (
    lat >= KENYA_BOUNDS.minLat &&
    lat <= KENYA_BOUNDS.maxLat &&
    lng >= KENYA_BOUNDS.minLng &&
    lng <= KENYA_BOUNDS.maxLng
  );
}

interface MapPickerProps {
  latitude?: number;
  longitude?: number;
  onChange: (lat: number, lng: number) => void;
}

export function MapPicker({ latitude, longitude, onChange }: MapPickerProps) {
  const ref = useRef<HTMLDivElement>(null);

  function handlePoint(e: PointerEvent<HTMLDivElement>) {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    const x = Math.min(Math.max(e.clientX - rect.left, 0), rect.width);
    const y = Math.min(Math.max(e.clientY - rect.top, 0), rect.height);
    const lng =
      KENYA_BOUNDS.minLng + (x / rect.width) * (KENYA_BOUNDS.maxLng - KENYA_BOUNDS.minLng);
    const lat =
      KENYA_BOUNDS.maxLat - (y / rect.height) * (KENYA_BOUNDS.maxLat - KENYA_BOUNDS.minLat);
    onChange(Number(lat.toFixed(4)), Number(lng.toFixed(4)));
  }

  const hasPin =
    typeof latitude === "number" &&
    typeof longitude === "number" &&
    isInKenya(latitude, longitude);

  const xPct = hasPin
    ? ((longitude! - KENYA_BOUNDS.minLng) / (KENYA_BOUNDS.maxLng - KENYA_BOUNDS.minLng)) * 100
    : 0;
  const yPct = hasPin
    ? ((KENYA_BOUNDS.maxLat - latitude!) / (KENYA_BOUNDS.maxLat - KENYA_BOUNDS.minLat)) * 100
    : 0;

  return (
    <div className="space-y-2">
      <div
        ref={ref}
        role="button"
        tabIndex={0}
        aria-label="Pick GPS coordinates within Kenya"
        onPointerDown={handlePoint}
        className="relative h-56 w-full cursor-crosshair overflow-hidden rounded-md border border-border bg-gradient-to-br from-emerald-50 to-emerald-100 dark:from-emerald-950 dark:to-emerald-900"
      >
        {/* Lat/Lng gridlines */}
        <div className="absolute inset-0 grid grid-cols-4 grid-rows-4 opacity-30">
          {Array.from({ length: 16 }).map((_, i) => (
            <div key={i} className="border border-emerald-700/30" />
          ))}
        </div>
        {/* Axis labels */}
        <span className="absolute left-1 top-1 text-[10px] text-emerald-900/70 dark:text-emerald-100/70">
          {KENYA_BOUNDS.minLng}°E, {KENYA_BOUNDS.maxLat}°N
        </span>
        <span className="absolute bottom-1 right-1 text-[10px] text-emerald-900/70 dark:text-emerald-100/70">
          {KENYA_BOUNDS.maxLng}°E, {KENYA_BOUNDS.minLat}°N
        </span>
        {hasPin ? (
          <div
            className="absolute -translate-x-1/2 -translate-y-full text-primary"
            style={{ left: `${xPct}%`, top: `${yPct}%` }}
          >
            <MapPin className="h-6 w-6 drop-shadow" fill="currentColor" />
          </div>
        ) : null}
      </div>
      <p className="text-xs text-muted-foreground">
        Click anywhere on the map to drop a pin. Bounds: lat −5 to 5, lng 33.5 to 42.
      </p>
    </div>
  );
}
