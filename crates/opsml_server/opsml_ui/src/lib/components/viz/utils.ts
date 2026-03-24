import { browser } from '$app/environment';

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

export interface ChartTheme {
  textColor: string;
  gridColor: string;
  axisColor: string;
  tooltipBg: string;
  tooltipBorder: string;
  tooltipText: string;
  zoomBorder: string;
  zoomBg: string;
}

export function getCssVar(name: string, fallback: string): string {
  if (!browser) return fallback;
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim() || fallback;
}

function isDarkMode(): boolean {
  if (!browser) return false;
  return document.documentElement.classList.contains('theme-dark');
}

export function getChartTheme(): ChartTheme {
  if (isDarkMode()) {
    return {
      textColor: getCssVar('--chart-text-color', 'oklch(80% 0.10 160)'),
      gridColor: getCssVar('--chart-grid-color', 'rgba(68, 204, 128, 0.15)'),
      axisColor: getCssVar('--chart-axis-color', 'oklch(70% 0.14 160)'),
      tooltipBg: getCssVar('--chart-tooltip-bg', 'oklch(15% 0.02 160)'),
      tooltipBorder: getCssVar('--chart-tooltip-border', 'rgba(68, 204, 128, 0.4)'),
      tooltipText: getCssVar('--chart-tooltip-text', 'oklch(85% 0.10 160)'),
      zoomBorder: getCssVar('--chart-zoom-border', 'oklch(75% 0.18 160)'),
      zoomBg: getCssVar('--chart-zoom-bg', 'rgba(68, 204, 128, 0.3)'),
    };
  }
  return {
    textColor: 'rgb(0, 0, 0)',
    gridColor: 'rgba(0, 0, 0, 0.1)',
    axisColor: 'rgb(0, 0, 0)',
    tooltipBg: 'rgba(255, 255, 255, 1)',
    tooltipBorder: 'rgb(0, 0, 0)',
    tooltipText: 'rgb(0, 0, 0)',
    zoomBorder: 'rgb(163, 135, 239)',
    zoomBg: 'rgba(163, 135, 239, 0.3)',
  };
}

// Generate an array of colors with optional alpha
export function generateColors(count: number, alpha: number = 1): string[] {
  const dark = isDarkMode();
  const colors = dark
    ? [
        `rgba(68, 204, 128, ${alpha})`,   // terminal green
        `rgba(204, 170, 68, ${alpha})`,    // amber
        `rgba(68, 180, 204, ${alpha})`,    // cyan
        `rgba(100, 220, 100, ${alpha})`,   // bright green
        `rgba(50, 160, 100, ${alpha})`,    // muted green
        `rgba(200, 80, 80, ${alpha})`,     // muted red
      ]
    : [
        `rgba(163, 135, 239, ${alpha})`, // primary-500
        `rgba(95, 214, 141, ${alpha})`,  // secondary-500
        `rgba(135, 170, 240, ${alpha})`, // tertiary-500
        `rgba(253, 220, 90, ${alpha})`,  // success-500
        `rgba(249, 178, 94, ${alpha})`,  // warning-500
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

export function getTooltip() {
  const theme = getChartTheme();
  return {
    cornerRadius: 1,
    backgroundColor: theme.tooltipBg,
    borderColor: theme.tooltipBorder,
    borderWidth: 1,
    enabled: true,
    titleColor: theme.tooltipText,
    titleFont: {
      size: 14,
    },
    bodyColor: theme.tooltipText,
    bodyFont: {
      size: 12,
    },
  };
}

export function getZoom() {
  const theme = getChartTheme();
  return {
    pan: {
      enabled: true,
      mode: "xy",
      modifierKey: "ctrl",
    },
    zoom: {
      mode: "xy",
      drag: {
        enabled: true,
        borderColor: theme.zoomBorder,
        borderWidth: 1,
        backgroundColor: theme.zoomBg,
      },
    },
  };
}

export function getLegend(
  showLegend: boolean = true,
  position: "top" | "bottom" | "left" | "right" = "bottom"
) {
  const theme = getChartTheme();
  return {
    display: showLegend,
    position: position,
    labels: {
      font: {
        size: 14,
      },
      color: theme.textColor,
    },
  };
}

export function getPlugins(
  showLegend: boolean = true,
  position: "top" | "bottom" | "left" | "right" = "bottom"
) {
  return {
    tooltip: getTooltip(),
    zoom: getZoom(),
    legend: getLegend(showLegend, position),
  };
}
