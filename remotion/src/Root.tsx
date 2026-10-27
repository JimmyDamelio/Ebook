import { Composition } from 'remotion';
import { Teaser } from './Teaser';

export const Root = () => (
  <Composition id="Teaser" component={Teaser} durationInFrames={330} fps={30} width={1080} height={1920} />
);
