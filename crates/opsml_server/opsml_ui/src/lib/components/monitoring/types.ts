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

export interface ConsoleDispatchConfig {
  enabled: boolean;
}

export interface SlackDispatchConfig {
  channel: string;
}

export interface OpsGenieDispatchConfig {
  team: string;
  priority: string;
}

export interface AlertDispatchConfig {
  Console?: ConsoleDispatchConfig;
  Slack?: SlackDispatchConfig;
  OpsGenie?: OpsGenieDispatchConfig;
}

// Add these type guard functions
export function hasConsoleConfig(config: AlertDispatchConfig): boolean {
  return config.Console !== undefined;
}

export function hasSlackConfig(config: AlertDispatchConfig): boolean {
  return config.Slack !== undefined;
}

export function hasOpsGenieConfig(config: AlertDispatchConfig): boolean {
  return config.OpsGenie !== undefined;
}
