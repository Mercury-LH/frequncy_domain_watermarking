import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { useI18n } from "../i18n";
import { SCENES, useStoryMetrics } from "./storyData";
import StoryStatic from "./StoryStatic";

gsap.registerPlugin(ScrollTrigger);

function usePinnedStory() {
  const [pinned, setPinned] = useState(true);
  useEffect(() => {
    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    const narrow = window.matchMedia("(max-width: 767px)");
    const update = () => setPinned(!media.matches && !narrow.matches);
    update();
    media.addEventListener("change", update);
    narrow.addEventListener("change", update);
    return () => {
      media.removeEventListener("change", update);
      narrow.removeEventListener("change", update);
    };
  }, []);
  return pinned;
}

function PinnedStory() {
  const { t } = useI18n();
  const metrics = useStoryMetrics();
  const containerRef = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    const context = gsap.context(() => {
      const panels = gsap.utils.toArray<HTMLElement>("[data-scene]");
      const frames = gsap.utils.toArray<HTMLElement>("[data-frame]");
      gsap.set(frames.slice(1), { autoAlpha: 0 });
      gsap.set(panels.slice(1), { autoAlpha: 0, y: 24 });
      const timeline = gsap.timeline({
        scrollTrigger: {
          trigger: container,
          start: "top top",
          end: `+=${SCENES.length * 90}%`,
          pin: true,
          scrub: 0.6,
        },
      });
      for (let index = 1; index < SCENES.length; index++) {
        timeline
          .to(panels[index - 1], { autoAlpha: 0, y: -24, duration: 0.4 }, index)
          .to(frames[index - 1], { autoAlpha: 0, duration: 0.4 }, index)
          .to(panels[index], { autoAlpha: 1, y: 0, duration: 0.4 }, index + 0.1)
          .to(frames[index], { autoAlpha: 1, duration: 0.4 }, index + 0.1);
      }
    }, container);
    return () => context.revert();
  }, []);

  return (
    <div ref={containerRef} className="relative min-h-screen">
      <div className="mx-auto grid h-screen max-w-5xl grid-cols-2 items-center gap-12 px-6">
        <div className="relative">
          {SCENES.map((scene) => {
            const copy = t.story[scene.key];
            return (
              <div key={scene.key} data-scene className="absolute inset-x-0 top-1/2 -translate-y-1/2">
                <h3 className="text-3xl text-ink">{copy.title}</h3>
                <p className="mt-3 max-w-md text-lg text-ink-muted">{copy.body}</p>
                {scene.metric && metrics && (
                  <p className="mt-4 font-display text-4xl tabular-nums text-brand">{scene.metric(metrics)}</p>
                )}
              </div>
            );
          })}
        </div>
        <div className="relative aspect-square">
          {SCENES.map((scene) => (
            <div key={scene.key} data-frame className="absolute inset-0 flex flex-col justify-center gap-3">
              <img src={scene.image} alt="" className="max-h-[70vh] w-full rounded-lg border border-line object-contain" />
              {scene.extraImage && (
                <img src={scene.extraImage} alt="" className="max-h-[20vh] w-full rounded-lg border border-line object-contain" />
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function Story() {
  const pinned = usePinnedStory();
  return <section id="story">{pinned ? <PinnedStory /> : <StoryStatic />}</section>;
}
