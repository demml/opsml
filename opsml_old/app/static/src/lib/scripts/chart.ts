export const grace = "10%";
export const legend = {
  display: false,
};

export const zoomOptions = {
  pan: {
    enabled: true,
    mode: "xy",
    modifierKey: "ctrl",
  },
  zoom: {
    mode: "xy",
    drag: {
      enabled: true,
      borderColor: "rgb(54, 162, 235)",
      borderWidth: 1,
      backgroundColor: "rgba(54, 162, 235, 0.3)",
    },
  },
};

export const handleResize = (chart) => {
  // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access, @typescript-eslint/no-unsafe-call
  chart.resize();
};
