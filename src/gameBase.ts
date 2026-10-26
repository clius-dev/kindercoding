// Vite's `base` (see vite.config.ts) makes this "/" in dev and "/kindercoding/" in prod,
// since the Pages deploy isn't served from the domain root.
export const GAME_BASE = `${import.meta.env.BASE_URL}game/`;
