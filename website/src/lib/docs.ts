import fs from "fs";
import path from "path";
import matter from "gray-matter";
import { remark } from "remark";
import remarkRehype from "remark-rehype";
import remarkGfm from "remark-gfm";
import rehypeStringify from "rehype-stringify";
import rehypeShiki from "@shikijs/rehype";
import { visit } from "unist-util-visit";

// Pre-initialize the processor to reuse it across requests
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

export interface DocMetadata {
  title: string;
  order?: number;
  [key: string]: unknown;
}

export interface DocContent {
  slug: string[];
  content: string;
  metadata: DocMetadata;
}

export interface SidebarItem {
  title: string;
  href: string;
  items?: SidebarItem[];
  order: number;
}

function stripOrderPrefix(name: string) {
  return name.replace(/^\d+-/, "");
}

function getOrder(name: string) {
  const match = name.match(/^(\d+)-/);
  return match ? parseInt(match[1], 10) : 999;
}

const contentDirectories = {
  docs: path.join(process.cwd(), "public/docs"),
  philosophy: path.join(process.cwd(), "philosophy"),
};

export async function getDocBySlug(
  slug: string[],
  type: keyof typeof contentDirectories = "docs"
): Promise<DocContent | null> {
  const baseDir = contentDirectories[type];
  // Decode slug components to handle URL-encoded characters
  const decodedSlug = slug.map((s) => decodeURIComponent(s));

  // Try exact match first
  let fullPath = path.join(baseDir, ...decodedSlug);
  if (!fullPath.endsWith(".md")) {
    fullPath += ".md";
  }

  // If exact match fails, try to find matching files/folders ignoring order prefix
  if (!fs.existsSync(fullPath)) {
    let currentPath = baseDir;
    for (const segment of decodedSlug) {
      if (!fs.existsSync(currentPath)) return null;
      const items = fs.readdirSync(currentPath);
      const match = items.find(
        (item) => stripOrderPrefix(item.replace(/\.md$/, "")) === segment
      );
      if (!match) return null;
      currentPath = path.join(currentPath, match);
    }
    fullPath = currentPath;
  }

  if (!fs.existsSync(fullPath)) {
    return null;
  }

  // Check if it's a directory, if so look for index.md or README.md?
  // For now assuming fullPath points to a file
  if (fs.statSync(fullPath).isDirectory()) {
    return null;
  }

  const fileContents = fs.readFileSync(fullPath, "utf8");
  const { data, content } = matter(fileContents);
  const processor = await getProcessor();
  const processedContent = await processor.process(content);
  const contentHtml = processedContent.toString();

  return {
    slug,
    content: contentHtml,
    metadata: data as DocMetadata,
  };
}

export function getAllDocs(
  lang: string,
  type: keyof typeof contentDirectories = "docs"
): DocContent[] {
  const baseDir = path.join(contentDirectories[type], lang);
  if (!fs.existsSync(baseDir)) return [];

  const docs: DocContent[] = [];

  function traverse(currentPath: string, currentSlug: string[]) {
    const items = fs.readdirSync(currentPath);

    for (const item of items) {
      if (item.startsWith(".")) continue;

      const fullPath = path.join(currentPath, item);
      const stat = fs.statSync(fullPath);

      if (stat.isDirectory()) {
        const slugPart = stripOrderPrefix(item);
        traverse(fullPath, [...currentSlug, slugPart]);
      } else if (item.endsWith(".md")) {
        const slugPart = stripOrderPrefix(item.replace(/\.md$/, ""));
        // Skip index/README if necessary, or handle them
        const slug = [...currentSlug, slugPart];

        // Simplified content loading (metadata only would be faster but we need full structure potentially)
        // For getAllDocs we mainly need slugs
        const fileContents = fs.readFileSync(fullPath, "utf8");
        const { data } = matter(fileContents);

        docs.push({
          slug,
          content: "", // Content not needed for listing
          metadata: data as DocMetadata,
        });
      }
    }
  }

  traverse(baseDir, [lang]);
  return docs;
}

export function getSidebar(
  lang: string,
  type: keyof typeof contentDirectories = "docs"
): SidebarItem[] {
  const baseDir = path.join(contentDirectories[type], lang);

  if (!fs.existsSync(baseDir)) {
    return [];
  }

  function getItems(dir: string, baseUrl: string): SidebarItem[] {
    const items = fs.readdirSync(dir);
    const sidebarItems: SidebarItem[] = [];

    items.forEach((item) => {
      if (item.startsWith(".")) return;

      const fullPath = path.join(dir, item);
      const stat = fs.statSync(fullPath);
      const order = getOrder(item);
      const name = stripOrderPrefix(item.replace(/\.md$/, ""));

      if (stat.isDirectory()) {
        const children = getItems(fullPath, `${baseUrl}/${name}`);
        if (children.length > 0) {
          let title = name.charAt(0).toUpperCase() + name.slice(1);
          const metaPath = path.join(fullPath, "_meta.json");

          if (fs.existsSync(metaPath)) {
            try {
              const metaContent = fs.readFileSync(metaPath, "utf8");
              const meta = JSON.parse(metaContent);
              if (meta.title) {
                title = meta.title;
              }
            } catch (e) {
              console.error(`Failed to parse meta file at ${metaPath}:`, e);
            }
          }

          sidebarItems.push({
            title,
            href: `${baseUrl}/${name}`,
            items: children.sort((a, b) => a.order - b.order),
            order,
          });
        }
      } else if (item.endsWith(".md")) {
        const fileContents = fs.readFileSync(fullPath, "utf8");
        const { data } = matter(fileContents);
        sidebarItems.push({
          title: data.title || name,
          href: `${baseUrl}/${name}`,
          order,
        });
      }
    });

    return sidebarItems.sort((a, b) => a.order - b.order);
  }

  // Base URL construction
  // The route structure is /[lang]/docs/... or /[lang]/philosophy/...
  const urlType = type === "docs" ? "docs" : "philosophy";
  return getItems(baseDir, `/${lang}/${urlType}`);
}
