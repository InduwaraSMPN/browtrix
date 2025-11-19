import TurndownService from "turndown";

export function captureSnapshot(): string {
  const turndownService = new TurndownService({
    headingStyle: "atx",
    codeBlockStyle: "fenced",
  });

  // Remove scripts, styles, and hidden elements to clean up the output
  turndownService.remove("script");
  turndownService.remove("style");
  turndownService.remove("noscript");
  
  return turndownService.turndown(document.body);
}
