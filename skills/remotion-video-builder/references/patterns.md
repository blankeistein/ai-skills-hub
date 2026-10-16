# Pola kode Remotion

Daftar isi: Root & durasi, Video.tsx, Scene Title, helper animasi, Audio, Transisi.

## Root.tsx - durasi dihitung dari data
```tsx
import { Composition } from 'remotion';
import { Video } from './Video';
import data from './data/scenes.json';

const { fps, width, height } = data.meta;
const total = data.scenes.reduce((s, sc) => s + Math.round(sc.durationSec * fps), 0);

export const RemotionRoot = () => (
  <Composition
    id="Main"
    component={Video}
    durationInFrames={total}
    fps={fps}
    width={width}
    height={height}
  />
);
```

## Video.tsx - scene berurutan + audio
```tsx
import { AbsoluteFill, Audio, Series, staticFile } from 'remotion';
import data from './data/scenes.json';
import { SceneRenderer } from './scenes/SceneRenderer';

export const Video = () => {
  const { fps } = data.meta;
  return (
    <AbsoluteFill style={{ backgroundColor: data.theme.bg }}>
      {data.audio?.music && (
        <Audio src={staticFile(data.audio.music)} volume={data.audio.musicVolume ?? 0.15} />
      )}
      {data.audio?.voiceover && <Audio src={staticFile(data.audio.voiceover)} />}
      <Series>
        {data.scenes.map((sc) => (
          <Series.Sequence key={sc.id} durationInFrames={Math.round(sc.durationSec * fps)}>
            <SceneRenderer scene={sc} />
          </Series.Sequence>
        ))}
      </Series>
    </AbsoluteFill>
  );
};
```

## scenes/SceneRenderer.tsx - pilih layout
```tsx
import { Title } from './Title';
export const SceneRenderer = ({ scene }: { scene: any }) => {
  switch (scene.layout) {
    case 'title':
    default:
      return <Title scene={scene} />;
  }
};
```
Tambahkan case untuk `list`, `stat`, `image-caption`, dst. sesuai kebutuhan.

## scenes/Title.tsx - animasi pop-in
```tsx
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import data from '../data/scenes.json';

export const Title = ({ scene }: { scene: { text: string; subtext?: string | null } }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const pop = spring({ frame, fps, config: { damping: 12, stiffness: 140 } });
  const fadeOut = interpolate(frame, [durationInFrames - 6, durationInFrames], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{ justifyContent: 'center', alignItems: 'center', padding: '8% 7%', opacity: fadeOut }}
    >
      <h1
        style={{
          color: data.theme.text,
          fontFamily: data.theme.fontHeading,
          fontSize: 96,
          textAlign: 'center',
          lineHeight: 1.15,
          transform: `scale(${interpolate(pop, [0, 1], [0.8, 1])})`,
          opacity: pop,
        }}
      >
        {scene.text}
      </h1>
    </AbsoluteFill>
  );
};
```

## Helper: muncul bertahap per kata (word-by-word)
```tsx
const words = text.split(' ');
words.map((w, i) => {
  const p = spring({ frame: frame - i * 4, fps });
  return <span key={i} style={{ opacity: p, display: 'inline-block', marginRight: 16,
    transform: `translateY(${(1 - p) * 30}px)` }}>{w}</span>;
});
```

## Font (Google Fonts)
```tsx
import { loadFont } from '@remotion/google-fonts/Poppins';
const { fontFamily } = loadFont();   // panggil di top-level file, pakai fontFamily di style
```
Nama font di theme harus sama dengan modul yang di-import; paling aman gunakan `fontFamily` hasil `loadFont()`.

## Transisi antar scene
```tsx
import { TransitionSeries, linearTiming } from '@remotion/transitions';
import { fade } from '@remotion/transitions/fade';

<TransitionSeries>
  <TransitionSeries.Sequence durationInFrames={90}><A /></TransitionSeries.Sequence>
  <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: 12 })} />
  <TransitionSeries.Sequence durationInFrames={90}><B /></TransitionSeries.Sequence>
</TransitionSeries>
```
Setiap transisi memotong durasi total sebesar `durationInFrames` transisi; kurangi dari `durationInFrames` Composition. Instal dengan `npx remotion add transitions` atau `npm i @remotion/transitions` sesuai versi Remotion proyek.
