import { remark } from "remark";
import remarkRehype from "remark-rehype";
import remarkGfm from "remark-gfm";
import rehypeStringify from "rehype-stringify";
import rehypeShiki from "@shikijs/rehype";
import { visit } from "unist-util-visit";

// Pre-initialize the processor to reuse it across renders
// UNIFIED_TYPES_COMPLEXITY: The return type of remark().use(...) chains is excessively complex to type statically.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
let memoizedProcessor: any = null;

async function getProcessor() {
  if (memoizedProcessor) return memoizedProcessor;

  memoizedProcessor = remark()
    .use(remarkGfm)
    .use(remarkRehype)
    .use(rehypeMermaid)
    .use(rehypeShiki, {
      theme: "vitesse-dark",
    })
    .use(rehypeStringify);

  return memoizedProcessor;
}

// Custom plugin to transform mermaid code blocks
function rehypeMermaid() {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return (tree: any) => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    visit(tree, "element", (node: any, index: any, parent: any) => {
      if (node.tagName === "pre" && node.children && node.children.length > 0) {
        const codeNode = node.children[0];
        if (
          codeNode.tagName === "code" &&
          codeNode.properties &&
          codeNode.properties.className &&
          Array.isArray(codeNode.properties.className) &&
          codeNode.properties.className.includes("language-mermaid")
        ) {
          const value = codeNode.children[0].value;

          parent.children[index] = {
            type: "element",
            tagName: "div",
            properties: { className: ["mermaid"] },
            children: [{ type: "text", value: value }],
          };
        }
      }
    });
  };
}

/**
 * Renders markdown content to HTML string
 * @param markdown Markdown content
 * @returns HTML string
 */
export async function renderMarkdown(markdown: string): Promise<string> {
  const processor = await getProcessor();
  const processedContent = await processor.process(markdown);
  return processedContent.toString();
}