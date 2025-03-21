export enum AlertDispatchType {
  Slack = "Slack",
  Console = "Console",
  OpsGenie = "OpsGenie",
}

export enum DriftType {
  Spc = "Spc",
  Psi = "Psi",
  Custom = "Custom",
}

export interface FeatureMap {
  features: Record<string, Record<string, number>>;
}

export enum TimeInterval {
  FiveMinutes = "5minute",
  FifteenMinutes = "15minute",
  ThirtyMinutes = "30minute",
  OneHour = "1hour",
  ThreeHours = "3hour",
  SixHours = "6hour",
  TwelveHours = "12hour",
  TwentyFourHours = "24hour",
  TwoDays = "2day",
  FiveDays = "5day",
}

export interface SlackDispatchConfig {
  channel: string;
}

export interface OpsGenieDispatchConfig {
  team: string;
}

export type AlertDispatchConfig =
  | { type: "Slack"; config: SlackDispatchConfig }
  | { type: "OpsGenie"; config: OpsGenieDispatchConfig }
  | { type: "Console" };
