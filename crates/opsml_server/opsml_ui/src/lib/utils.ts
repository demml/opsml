export enum RegistryType {
  Data = "Data",
  Model = "Model",
  Experiment = "Experiment",
  Prompt = "Prompt",
}

export function getRegistryTypeLowerCase(type: RegistryType): string {
  return type.toLowerCase();
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
