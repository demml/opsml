export type DateTime = string;

/**
 * Represents the Rust 'serde_json::Value' type.
 */
export type JsonValue =
  | string
  | number
  | boolean
  | null
  | { [key: string]: JsonValue }
  | JsonValue[];
