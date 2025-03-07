export enum RegistryType {
  Data = "Data",
  Model = "Model",
  Experiment = "Experiment",
  Prompt = "Prompt",
}

export function goTop() {
  document.body.scrollIntoView();
}

export function calculateTimeBetween(created_at: string): string {
  const presentDate: Date = new Date();
  const date1: Date = new Date(created_at);

  const hours = Math.abs(presentDate.getTime() - date1.getTime()) / 3600000;

  if (hours < 1) {
    const minutes = Math.round(hours * 60);
    return `${minutes} minutes ago`;
  } else if (hours > 24) {
    const days = Math.floor(hours / 24);
    return `${days} days ago`;
  }
  return `${Math.round(hours)} hours ago`;
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
