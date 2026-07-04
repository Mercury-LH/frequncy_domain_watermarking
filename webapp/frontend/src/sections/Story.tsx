import { useI18n } from "../i18n";
import { SCENES, useStoryMetrics } from "./storyData";

// A calm, normal-flow narrative — no scroll pinning or scrubbing (which jittered).
// Scenes alternate image/text on desktop for editorial rhythm; stacked on mobile.
export default function Story() {
  const { t } = useI18n();
  const metrics = useStoryMetrics();

  return (
    <section id="story" className="mx-auto max-w-4xl px-4 py-16 sm:px-6 sm:py-24">
      <div className="space-y-16 sm:space-y-24">
        {SCENES.map((scene, index) => {
          const copy = t.story[scene.key];
          const flip = index % 2 === 1;
          return (
            <figure
              key={scene.key}
              className="grid items-center gap-6 sm:grid-cols-2 sm:gap-10"
            >
              <div className={flip ? "sm:order-2" : ""}>
                <div className="flex flex-col gap-3 rounded-xl border border-line bg-surface p-3">
                  <img
                    src={scene.image}
                    alt={copy.title}
                    loading="lazy"
                    className="mx-auto max-h-[320px] w-auto rounded-lg object-contain"
                  />
                  {scene.extraImage && (
                    <img
                      src={scene.extraImage}
                      alt=""
                      loading="lazy"
                      className="mx-auto max-h-[120px] w-auto rounded-lg object-contain"
                    />
                  )}
                </div>
              </div>
              <figcaption className={flip ? "sm:order-1" : ""}>
                <h3 className="text-2xl text-ink sm:text-3xl">{copy.title}</h3>
                <p className="mt-3 max-w-md text-base leading-relaxed text-ink-muted sm:text-lg">
                  {copy.body}
                </p>
                {scene.metric && metrics && (
                  <p className="mt-4 font-display text-3xl tabular-nums text-brand sm:text-4xl">
                    {scene.metric(metrics)}
                  </p>
                )}
              </figcaption>
            </figure>
          );
        })}
      </div>
    </section>
  );
}
