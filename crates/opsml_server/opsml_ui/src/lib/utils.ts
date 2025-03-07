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
