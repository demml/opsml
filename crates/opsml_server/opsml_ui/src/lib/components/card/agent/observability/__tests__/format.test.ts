import { describe, it, expect } from 'vitest';
import { fmtInt, fmtCompact, fmtPct, fmtMs, fmtUsd } from '../format';

describe('fmtInt', () => {
  it('formats integer with locale separators', () => {
    expect(fmtInt(1200)).toBe('1,200');
  });

  it('handles zero', () => {
    expect(fmtInt(0)).toBe('0');
  });
});

describe('fmtCompact', () => {
  it('abbreviates large numbers', () => {
    expect(fmtCompact(1500)).toBe('1.5K');
  });

  it('passes through small numbers', () => {
    expect(fmtCompact(100)).toBe('100');
  });
});

describe('fmtPct', () => {
  it('converts fraction to percentage', () => {
    expect(fmtPct(0.0312)).toBe('3.12%');
  });

  it('respects digits param', () => {
    expect(fmtPct(0.5, 0)).toBe('50%');
  });
});

describe('fmtMs', () => {
  it('returns dash for null', () => {
    expect(fmtMs(null)).toBe('—');
  });

  it('returns dash for undefined', () => {
    expect(fmtMs(undefined)).toBe('—');
  });

  it('formats sub-second as ms', () => {
    expect(fmtMs(250)).toBe('250 ms');
  });

  it('formats over 1000ms as seconds', () => {
    expect(fmtMs(2500)).toBe('2.50 s');
  });
});

describe('fmtUsd', () => {
  it('returns dash for null', () => {
    expect(fmtUsd(null)).toBe('—');
  });

  it('formats small amounts with $', () => {
    expect(fmtUsd(0.42)).toBe('$0.42');
  });

  it('formats large amounts in thousands', () => {
    expect(fmtUsd(1500)).toBe('$1.50k');
  });
});
