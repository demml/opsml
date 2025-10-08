/**
 * Manages large file display strategies (preview, virtual scrolling)
 */
export class LargeFileManager {
  private readonly LARGE_FILE_THRESHOLD = 50000; // 50KB
  private readonly VIRTUAL_SCROLL_THRESHOLD = 200000; // 200KB
  private readonly PREVIEW_LINES = 100;

  content: string;
  showFullContent = $state(false);

  constructor(content: string) {
    this.content = content;
  }

  get isLargeFile(): boolean {
    return this.content.length > this.LARGE_FILE_THRESHOLD;
  }

  get needsVirtualScrolling(): boolean {
    return this.content.length > this.VIRTUAL_SCROLL_THRESHOLD;
  }

  get fileSizeKB(): number {
    return this.content.length / 1024;
  }

  getPreviewContent(): string {
    const lines = this.content.split("\n");
    if (lines.length <= this.PREVIEW_LINES) return this.content;
    return lines.slice(0, this.PREVIEW_LINES).join("\n");
  }

  toggleFullContent() {
    this.showFullContent = !this.showFullContent;
  }
}

export function useLargeFileManager(content: string) {
  return new LargeFileManager(content);
}
