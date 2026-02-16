export enum RegistryType {
  Data = "data",
  Model = "model",
  Experiment = "experiment",
  Prompt = "prompt",
  Service = "service",
  Mcp = "mcp",
  Agent = "agent",
}

export function getRegistryTypeLowerCase(type: RegistryType): string {
  let name = type.toLowerCase();

  return name;
}

export function getRegistryTypeUpperCase(type: RegistryType): string {
  let name = type.charAt(0).toUpperCase() + type.slice(1).toLowerCase();
  return name;
}

export function getRegistryPath(type: RegistryType): string {
  switch (type) {
    case RegistryType.Data:
      return "data";
    case RegistryType.Model:
      return "model";
    case RegistryType.Experiment:
      return "experiment";
    case RegistryType.Prompt:
      return "genai/prompt";
    case RegistryType.Service:
      return "service";
    case RegistryType.Mcp:
      return "genai/mcp";
    case RegistryType.Agent:
      return "genai/agent";
    default:
      return "";
  }
}

export function getRegistryFromString(type: string): RegistryType | undefined {
  switch (type.toLowerCase()) {
    case "data":
      return RegistryType.Data;
    case "model":
      return RegistryType.Model;
    case "experiment":
      return RegistryType.Experiment;
    case "prompt":
      return RegistryType.Prompt;
    case "service":
      return RegistryType.Service;
    case "mcp":
      return RegistryType.Mcp;
    case "agent":
      return RegistryType.Agent;
    default:
      return undefined;
  }
}

export function getRegistryTableName(type: RegistryType): string {
  return "opsml_" + type.toLowerCase() + "_registry";
}

export function goTop() {
  document.body.scrollIntoView();
}

export function calculateTimeBetween(created_at: string): string {
  if (!created_at.endsWith("Z")) {
    created_at += "Z";
  }

  const presentDate = Date.now();
  const date1 = new Date(created_at).getTime();

  // Calculate difference in milliseconds
  const diffMs = presentDate - date1;
  const diffMinutes = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffMinutes < 60) {
    return `${diffMinutes} minutes ago`;
  } else if (diffHours < 24) {
    return `${diffHours} hours ago`;
  }
  return `${diffDays} days ago`;
}

export function delay(fn: any, ms: number) {
  let timer = 0;
  return function (...args: any) {
    clearTimeout(timer);

    // @ts-expect-error "ignore"
    // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access,  @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-argument
    timer = window.setTimeout(fn.bind(this, ...args), ms || 0);
  };
}

export function getMaxDataPoints(): number {
  if (window.innerWidth < 640) {
    return 100;
  } else if (window.innerWidth < 768) {
    return 200;
  } else if (window.innerWidth < 1024) {
    return 400;
  } else if (window.innerWidth < 1280) {
    return 600;
  } else if (window.innerWidth < 1536) {
    return 800;
  } else {
    return 1000;
  }
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number,
): (...args: Parameters<T>) => void {
  let timeout: number;
  return (...args: Parameters<T>) => {
    window.clearTimeout(timeout);
    timeout = window.setTimeout(() => func(...args), wait);
  };
}
