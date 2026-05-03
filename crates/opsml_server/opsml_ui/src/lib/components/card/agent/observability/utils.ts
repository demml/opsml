import type { PromptCard } from '$lib/components/card/card_interfaces/promptcard';
import type { EvalProfileOption } from './types';

const VALID_SCOUTER_INTERVALS = new Set([
  'second', 'minute', 'hour', 'day', 'week', 'month', 'year',
]);

/**
 * Convert a PostgreSQL-style interval string (e.g. "1 hours", "30 minutes")
 * to a Scouter BucketInterval enum value ("hour", "minute", etc.).
 */
export function toScouterInterval(interval: string): string {
  if (VALID_SCOUTER_INTERVALS.has(interval)) return interval;
  const lower = interval.toLowerCase();
  if (lower.includes('second')) return 'minute';
  if (lower.includes('minute')) return 'minute';
  if (lower.includes('hour')) return 'hour';
  if (lower.includes('day')) return 'day';
  if (lower.includes('week')) return 'week';
  if (lower.includes('month')) return 'month';
  if (lower.includes('year')) return 'year';
  return 'hour';
}

export function toEvalProfileOptions(cards: PromptCard[]): EvalProfileOption[] {
  return cards
    .filter((pc) => !!pc.eval_profile)
    .map((pc) => ({
      uid: pc.eval_profile!.config.uid,
      alias: pc.eval_profile!.alias ?? null,
      name: pc.name,
    }));
}
