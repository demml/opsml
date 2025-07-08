export enum RegistryType {
  Data = "Data",
  Model = "Model",
  Experiment = "Experiment",
  Prompt = "Prompt",
  Service = "Service",
}

export function getRegistryTypeLowerCase(type: RegistryType): string {
  let name = type.toLowerCase();

  // if registry_name == "prompt" change to genai
  // this is only temporary until we start having both agent and prompt registries
  if (name === "prompt") {
    name = "genai";
  }

  return name;
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
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: number;
  return (...args: Parameters<T>) => {
    window.clearTimeout(timeout);
    timeout = window.setTimeout(() => func(...args), wait);
  };
}
