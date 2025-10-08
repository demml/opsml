/**
 * Virtual scrolling implementation for large files
 */
export class VirtualScrollManager {
  private content: string = "";
  private lines: string[] = [];

  readonly lineHeight = 20;
  readonly bufferLines = 20;

  scrollTop = $state(0);
  containerHeight = $state(600);
  visibleContent = $state("");
  totalHeight = $derived(this.lines.length * this.lineHeight);

  constructor(content: string) {
    this.updateContent(content);
  }

  updateContent(newContent: string) {
    this.content = newContent;
    this.lines = newContent.split("\n");
    this.updateVisibleContent();
  }

  handleScroll = (e: Event) => {
    const target = e.target as HTMLElement;
    this.scrollTop = target.scrollTop;
    this.updateVisibleContent();
  };

  private updateVisibleContent() {
    const startLine = Math.max(
      0,
      Math.floor(this.scrollTop / this.lineHeight) - this.bufferLines
    );
    const visibleLines =
      Math.ceil(this.containerHeight / this.lineHeight) + this.bufferLines * 2;
    const endLine = Math.min(this.lines.length, startLine + visibleLines);

    this.visibleContent = this.lines.slice(startLine, endLine).join("\n");
  }

  get startingLineNumber(): number {
    return Math.max(
      1,
      Math.floor(this.scrollTop / this.lineHeight) - this.bufferLines + 1
    );
  }

  get topOffset(): number {
    return (
      Math.max(
        0,
        Math.floor(this.scrollTop / this.lineHeight) - this.bufferLines
      ) * this.lineHeight
    );
  }
}

export function useVirtualScrolling(content: string) {
  return new VirtualScrollManager(content);
}
