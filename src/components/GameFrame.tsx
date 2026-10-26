import { useEffect, useRef } from 'react';
import { progressRepository } from '../storage/localStorageRepository';

interface StageCompleteMessage {
  source: 'kindercoding-game';
  type: 'stageComplete';
  theme: string;
  stage: string;
}

function isStageCompleteMessage(data: unknown): data is StageCompleteMessage {
  return !!data && typeof data === 'object' && (data as { source?: unknown }).source === 'kindercoding-game' && (data as { type?: unknown }).type === 'stageComplete';
}

export default function GameFrame({ email }: { email: string }) {
  const iframeRef = useRef<HTMLIFrameElement>(null);

  useEffect(() => {
    function onMessage(e: MessageEvent) {
      if (!isStageCompleteMessage(e.data)) return;
      progressRepository.recordCompletion(email, e.data.theme, e.data.stage);
    }
    window.addEventListener('message', onMessage);
    return () => window.removeEventListener('message', onMessage);
  }, [email]);

  return (
    <iframe
      ref={iframeRef}
      src="/game/B_0_main/main.html"
      title="KinderCoding"
      allow="autoplay"
      style={{ border: 'none', width: '100vw', height: '100vh', display: 'block' }}
    />
  );
}
