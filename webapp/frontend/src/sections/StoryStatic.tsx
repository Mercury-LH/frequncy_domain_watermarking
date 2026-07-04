import { useI18n } from "../i18n";
import { SCENES, useStoryMetrics } from "./storyData";

export default function StoryStatic() {
  const { t } = useI18n();
  const metrics = useStoryMetrics();
  return (
    <div className="mx-auto max-w-2xl space-y-16 px-4 py-16 sm:px-6">
      {SCENES.map((scene) => {
        const copy = t.story[scene.key];
        return (
          <figure key={scene.key} className="space-y-3">
            <img src={scene.image} alt={copy.title} className="w-full rounded-lg border border-line" loading="lazy" />
            {scene.extraImage && <img src={scene.extraImage} alt="" className="w-full rounded-lg border border-line" loading="lazy" />}
            <figcaption>
              <h3 className="text-2xl text-ink">{copy.title}</h3>
              <p className="mt-1 text-ink-muted">{copy.body}</p>
              {scene.metric && metrics && (
                <p className="mt-2 font-display text-3xl tabular-nums text-brand">{scene.metric(metrics)}</p>
              )}
            </figcaption>
          </figure>
        );
      })}
    </div>
  );
}
