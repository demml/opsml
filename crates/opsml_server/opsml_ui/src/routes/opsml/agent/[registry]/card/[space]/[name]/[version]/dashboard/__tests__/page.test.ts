import { describe, it, expect } from 'vitest';
import { toEvalProfileOptions } from '../+page';
import { RegistryType } from '$lib/utils';
import type { PromptCard } from '$lib/components/card/card_interfaces/promptcard';

function makeCard(overrides: Partial<PromptCard> = {}): PromptCard {
  return {
    name: 'my-prompt',
    space: 'test',
    version: '1.0.0',
    uid: 'uid-1',
    tags: [],
    metadata: {},
    registry_type: RegistryType.Prompt,
    app_env: 'dev',
    created_at: '2026-01-01T00:00:00Z',
    is_card: true,
    opsml_version: '0.1.0',
    prompt: {} as never,
    ...overrides,
  };
}

describe('toEvalProfileOptions', () => {
  it('returns empty array when no cards have eval_profile', () => {
    const cards = [makeCard(), makeCard({ name: 'other' })];
    expect(toEvalProfileOptions(cards)).toEqual([]);
  });

  it('includes only cards that have eval_profile', () => {
    const withProfile = makeCard({
      name: 'with-profile',
      eval_profile: {
        alias: 'my-alias',
        config: { uid: 'profile-uid-1' },
      } as never,
    });
    const withoutProfile = makeCard({ name: 'no-profile' });
    const result = toEvalProfileOptions([withProfile, withoutProfile]);
    expect(result).toHaveLength(1);
    expect(result[0].uid).toBe('profile-uid-1');
  });

  it('maps alias and name correctly', () => {
    const card = makeCard({
      name: 'my-prompt',
      eval_profile: {
        alias: 'eval-alias',
        config: { uid: 'uid-abc' },
      } as never,
    });
    const result = toEvalProfileOptions([card]);
    expect(result[0]).toEqual({ uid: 'uid-abc', alias: 'eval-alias', name: 'my-prompt' });
  });

  it('sets alias to null when eval_profile.alias is undefined', () => {
    const card = makeCard({
      name: 'my-prompt',
      eval_profile: {
        alias: undefined,
        config: { uid: 'uid-xyz' },
      } as never,
    });
    const result = toEvalProfileOptions([card]);
    expect(result[0].alias).toBeNull();
  });
});
