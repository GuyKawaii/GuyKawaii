export interface Profile {
  username: string;
  avatar: string;
  collectedAt: string;
  totalLines: number;
  publicRepos: number;
  stars: number;
  commits: number;
}
export function validateProfile(value: unknown): Profile {
  if (!value || typeof value !== 'object') throw new Error('Invalid profile snapshot');
  const data = value as Record<string, unknown>;
  for (const key of ['username','avatar','collectedAt']) {
    if (typeof data[key] !== 'string' || !data[key]) throw new Error(`Invalid snapshot field: ${key}`);
  }
  if (!(data.avatar as string).startsWith('data:image/png;base64,')) throw new Error('Snapshot avatar must be embedded PNG');
  for (const key of ['totalLines','publicRepos','stars','commits']) {
    if (!Number.isSafeInteger(data[key]) || Number(data[key]) < 0) throw new Error(`Invalid snapshot field: ${key}`);
  }
  // Explicit allowlist prevents private repository metadata from reaching the renderer.
  return Object.fromEntries(['username','avatar','collectedAt','totalLines','publicRepos','stars','commits'].map(key=>[key,data[key]])) as unknown as Profile;
}
