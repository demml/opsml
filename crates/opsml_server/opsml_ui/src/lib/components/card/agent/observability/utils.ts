import type { PromptCard } from '$lib/components/card/card_interfaces/promptcard';
import type { EvalProfileOption } from './types';

export function toEvalProfileOptions(cards: PromptCard[]): EvalProfileOption[] {
  return cards
    .filter((pc) => !!pc.eval_profile)
    .map((pc) => ({
      uid: pc.eval_profile!.config.uid,
      alias: pc.eval_profile!.alias ?? null,
      name: pc.name,
    }));
}
