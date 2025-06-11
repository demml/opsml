export interface ChartjsLineDataset {
  label: string;
  data: number[];
  borderColor: string;
  backgroundColor: string;
  pointRadius: number;
  fill: boolean;
}

export interface ChartjsBarDataset {
  label: string;
  data: number[];
  backgroundColor: string;
  borderColor: string;
  borderWidth: number;
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

export const tooltip = {
  cornerRadius: 1,
  backgroundColor: "rgba(255, 255, 255, 1)",
  borderColor: "rgb(0, 0, 0)",
  borderWidth: 1,
  enabled: true,
  titleColor: "rgb(0, 0, 0)",
  titleFont: {
    size: 14,
  },
  bodyColor: "rgb(0, 0, 0)",
  bodyFont: {
    size: 12,
  },
};

export const zoom = {
  pan: {
    enabled: true,
    mode: "xy",
    modifierKey: "ctrl",
  },
  zoom: {
    mode: "xy",
    drag: {
      enabled: true,
      borderColor: "rgb(163, 135, 239)",
      borderWidth: 1,
      backgroundColor: "rgba(163, 135, 239, 0.3)",
    },
  },
};

export function getLegend(
  showLegend: boolean = true,
  position: "top" | "bottom" | "left" | "right" = "bottom"
) {
  return {
    display: showLegend,
    position: position,
    labels: {
      font: {
        size: 14, // Increase legend font size (in pixels)
      },
      color: "rgb(0, 0, 0)",
    },
  };
}

export function getPlugins(
  showLegend: boolean = true,
  position: "top" | "bottom" | "left" | "right" = "bottom"
) {
  return {
    tooltip,
    zoom,
    legend: getLegend(showLegend, position),
  };
}
