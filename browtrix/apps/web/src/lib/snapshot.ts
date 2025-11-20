export function captureSnapshot(): string {
	// Create a clone of the document to avoid modifying the original
	const clone = document.cloneNode(true) as Document;

	// Remove scripts, styles, and hidden elements to clean up the output
	const elementsToRemove = clone.querySelectorAll(
		'script, style, noscript, [style*="display: none"], [hidden]',
	);
	elementsToRemove.forEach((el) => el.remove());

	// Return the HTML content
	return clone.documentElement.outerHTML;
}
