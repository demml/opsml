export interface ChartjsLineDataset {
  label: string;
  data: number[];
  borderColor: string;
  backgroundColor: string;
  pointRadius: number;
  fill: boolean;
}

// Generate an array of colors with optional alpha
export function generateColors(count: number, alpha: number = 1): string[] {
  const colors = [
    `rgba(163, 135, 239, ${alpha})`, // primary-500
    `rgba(95, 214, 141, ${alpha})`, // secondary-500
    `rgba(135, 170, 240, ${alpha})`, // tertiary-500
    `rgba(253, 220, 90, ${alpha})`, // success-500
    `rgba(249, 178, 94, ${alpha})`, // warning-500
    `rgba(254, 108, 107, ${alpha})`, // error-500
  ];

  return Array(count)
    .fill(null)
    .map((_, i) => colors[i % colors.length]);
}

export function handleResize(chart: any) {
  if (chart.canvas) {
    chart.resize();
  }
}
