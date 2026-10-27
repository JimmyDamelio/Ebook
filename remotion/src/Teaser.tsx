import { AbsoluteFill, Audio, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';

const C = { paper: '#F3ECDF', ink: '#2F3A33', sage: '#5C7658', terra: '#C77B5C', blush: '#E9BCA4' };

const fonts = `
@font-face{font-family:'Fraunces';src:url(${staticFile('fraunces.woff2')}) format('woff2');font-weight:100 900}
@font-face{font-family:'Fraunces';font-style:italic;src:url(${staticFile('fraunces-italic.woff2')}) format('woff2');font-weight:100 900}`;

const Line: React.FC<{ text: string; italic?: boolean; color?: string; size?: number }> = ({ text, italic, color = C.ink, size = 96 }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const k = spring({ frame: f, fps, config: { damping: 200 } });
  return (
    <div style={{ fontFamily: 'Fraunces', fontWeight: 300, fontStyle: italic ? 'italic' : 'normal', fontSize: size, color, textAlign: 'center',
      opacity: k, transform: `translateY(${(1 - k) * 40}px)`, filter: `blur(${(1 - k) * 8}px)`, padding: '0 80px', lineHeight: 1.15 }}>
      {text}
    </div>
  );
};

export const Teaser = () => {
  const f = useCurrentFrame();
  const blob = interpolate(f, [0, 330], [0.9, 1.15]);
  return (
    <AbsoluteFill style={{ background: C.paper }}>
      <style>{fonts}</style>
      <AbsoluteFill style={{ alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ width: 900, height: 900, borderRadius: '50%', background: C.blush, opacity: 0.35, filter: 'blur(90px)', transform: `scale(${blob})` }} />
      </AbsoluteFill>
      <Audio src={staticFile('voice.wav')} />
      <AbsoluteFill style={{ justifyContent: 'center', gap: 40 }}>
        <Sequence from={0} durationInFrames={75} layout="none"><Line text="Awake at 3 a.m., again." italic /></Sequence>
        <Sequence from={75} durationInFrames={70} layout="none"><Line text="Something feels different." /></Sequence>
        <Sequence from={145} durationInFrames={185} layout="none">
          <Line text="The Perimenopause Companion" size={104} />
          <Sequence from={30} layout="none"><Line text="See the pattern. Walk in with a clear picture." italic color={C.sage} size={64} /></Sequence>
          <Sequence from={80} layout="none"><Line text="sageandseason.gumroad.com" color={C.terra} size={52} /></Sequence>
        </Sequence>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
