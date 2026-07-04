import { useEffect, useState } from "react";

export type StoryMetrics = { psnr: number; ssim: number; nc: number };

export type SceneKey = "s1" | "s2" | "s3" | "s4" | "s5" | "s6";

export const SCENES: {
  key: SceneKey;
  image: string;
  extraImage?: string;
  metric?: (m: StoryMetrics) => string;
}[] = [
  { key: "s1", image: "/story/01-photo.png" },
  { key: "s2", image: "/story/02-spectrum.png" },
  { key: "s3", image: "/story/03-spectrum-marked.png" },
  { key: "s4", image: "/story/04-watermarked.png", extraImage: "/story/04-diff20.png", metric: (m) => `PSNR ${m.psnr} dB` },
  { key: "s5", image: "/story/05-attacked.png" },
  { key: "s6", image: "/story/06-extracted.png", metric: (m) => `NC ${m.nc}` },
];

export function useStoryMetrics(): StoryMetrics | null {
  const [metrics, setMetrics] = useState<StoryMetrics | null>(null);
  useEffect(() => {
    fetch("/story/story.json")
      .then((r) => r.json())
      .then(setMetrics)
      .catch(() => setMetrics(null));
  }, []);
  return metrics;
}
