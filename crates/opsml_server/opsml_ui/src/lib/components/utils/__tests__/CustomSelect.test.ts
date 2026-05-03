import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/svelte";
import CustomSelect from "../CustomSelect.svelte";

const OPTIONS = [
  { value: "gpt-4o", label: "gpt-4o" },
  { value: "claude-3-5-sonnet", label: "claude-3-5-sonnet" },
  { value: "gpt-4o-mini", label: "gpt-4o-mini" },
];

describe("CustomSelect — trigger label", () => {
  it("shows placeholder when no value selected", () => {
    render(CustomSelect, {
      props: { label: "Model", options: OPTIONS, value: null, onChange: vi.fn() },
    });
    expect(screen.getByRole("button", { name: "Model" })).toHaveTextContent("all");
  });

  it("shows selected option label when value is set", () => {
    render(CustomSelect, {
      props: {
        label: "Model",
        options: OPTIONS,
        value: "gpt-4o",
        onChange: vi.fn(),
      },
    });
    expect(screen.getByRole("button", { name: "Model" })).toHaveTextContent("gpt-4o");
  });
});

describe("CustomSelect — dropdown open/close", () => {
  it("popover is hidden on mount", () => {
    render(CustomSelect, {
      props: { label: "Model", options: OPTIONS, value: null, onChange: vi.fn() },
    });
    expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
  });

  it("clicking trigger opens the popover", async () => {
    render(CustomSelect, {
      props: { label: "Model", options: OPTIONS, value: null, onChange: vi.fn() },
    });
    await fireEvent.click(screen.getByRole("button", { name: "Model" }));
    expect(screen.getByRole("listbox")).toBeInTheDocument();
  });

  it("clicking trigger again closes the popover", async () => {
    render(CustomSelect, {
      props: { label: "Model", options: OPTIONS, value: null, onChange: vi.fn() },
    });
    const trigger = screen.getByRole("button", { name: "Model" });
    await fireEvent.click(trigger);
    await fireEvent.click(trigger);
    expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
  });

  it("Escape key closes the popover", async () => {
    render(CustomSelect, {
      props: { label: "Model", options: OPTIONS, value: null, onChange: vi.fn() },
    });
    await fireEvent.click(screen.getByRole("button", { name: "Model" }));
    await fireEvent.keyDown(screen.getByRole("button", { name: "Model" }), {
      key: "Escape",
    });
    expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
  });
});

describe("CustomSelect — (1) filter state update: onChange fires with correct value", () => {
  it("calls onChange with selected option value", async () => {
    const onChange = vi.fn();
    render(CustomSelect, {
      props: { label: "Model", options: OPTIONS, value: null, onChange },
    });
    await fireEvent.click(screen.getByRole("button", { name: "Model" }));
    await fireEvent.click(screen.getByRole("option", { name: "gpt-4o" }));
    expect(onChange).toHaveBeenCalledOnce();
    expect(onChange).toHaveBeenCalledWith("gpt-4o");
  });

  it("calls onChange with null when 'all' option is selected", async () => {
    const onChange = vi.fn();
    render(CustomSelect, {
      props: { label: "Model", options: OPTIONS, value: "gpt-4o", onChange },
    });
    await fireEvent.click(screen.getByRole("button", { name: "Model" }));
    await fireEvent.click(screen.getByRole("option", { name: "all" }));
    expect(onChange).toHaveBeenCalledWith(null);
  });

  it("closes popover after selection", async () => {
    render(CustomSelect, {
      props: { label: "Model", options: OPTIONS, value: null, onChange: vi.fn() },
    });
    await fireEvent.click(screen.getByRole("button", { name: "Model" }));
    await fireEvent.click(screen.getByRole("option", { name: "gpt-4o" }));
    expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
  });
});

describe("CustomSelect — (3) active filter displayed on trigger immediately", () => {
  it("trigger label updates immediately after selection (optimistic localValue)", async () => {
    const onChange = vi.fn();
    render(CustomSelect, {
      props: { label: "Model", options: OPTIONS, value: null, onChange },
    });
    await fireEvent.click(screen.getByRole("button", { name: "Model" }));
    await fireEvent.click(screen.getByRole("option", { name: "claude-3-5-sonnet" }));
    // Label must update without waiting for parent to echo back applied_filters
    expect(screen.getByRole("button", { name: "Model" })).toHaveTextContent(
      "claude-3-5-sonnet",
    );
  });

  it("trigger label reverts to placeholder when 'all' selected", async () => {
    render(CustomSelect, {
      props: { label: "Model", options: OPTIONS, value: "gpt-4o", onChange: vi.fn() },
    });
    await fireEvent.click(screen.getByRole("button", { name: "Model" }));
    await fireEvent.click(screen.getByRole("option", { name: "all" }));
    expect(screen.getByRole("button", { name: "Model" })).toHaveTextContent("all");
  });
});

describe("CustomSelect — disabled state", () => {
  it("disabled trigger does not open popover", async () => {
    render(CustomSelect, {
      props: {
        label: "Profile",
        options: OPTIONS,
        value: "gpt-4o",
        disabled: true,
        onChange: vi.fn(),
      },
    });
    await fireEvent.click(screen.getByRole("button", { name: "Profile" }));
    expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
  });

  it("disabled trigger does not call onChange", async () => {
    const onChange = vi.fn();
    render(CustomSelect, {
      props: {
        label: "Profile",
        options: OPTIONS,
        value: "gpt-4o",
        disabled: true,
        onChange,
      },
    });
    await fireEvent.click(screen.getByRole("button", { name: "Profile" }));
    expect(onChange).not.toHaveBeenCalled();
  });
});
