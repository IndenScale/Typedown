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

const docsDirectory = path.join(process.cwd(), "docs");

// Custom plugin to transform mermaid code blocks
function rehypeMermaid() {
  return (tree: any) => {
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
  [key: string]: any;
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
  docs: path.join(process.cwd(), "docs"),
  philosophy: path.join(process.cwd(), "philosophy"),
};

export async function getDocBySlug(slug: string[], type: keyof typeof contentDirectories = "docs"): Promise<DocContent | null> {
  const baseDir = contentDirectories[type];
  // Decode slug components to handle URL-encoded characters
  const decodedSlug = slug.map(s => decodeURIComponent(s));

  let currentPath = baseDir;
  for (const part of decodedSlug) {
    if (fs.existsSync(currentPath) && fs.statSync(currentPath).isDirectory()) {
      const entries = fs.readdirSync(currentPath);
      const entry = entries.find(e => stripOrderPrefix(e).replace(/\.md$/, "") === part);
      if (entry) {
        currentPath = path.join(currentPath, entry);
        continue;
      }
    }
    currentPath = path.join(currentPath, part);
  }

  const fullPath = currentPath;

  let filePath = fullPath.endsWith(".md") ? fullPath : `${fullPath}.md`;
  
  if (!fs.existsSync(filePath)) {
    const indexFallback = path.join(fullPath, "index.md");
    if (fs.existsSync(indexFallback)) {
      filePath = indexFallback;
    } else {
      // Try to find file with original name (in case stripOrderPrefix logic failed or is needed differently)
      // This is a simple fallback. The mapping logic above is usually correct.
      return null;
    }
  }

  const fileContents = fs.readFileSync(filePath, "utf8");
  const { data, content } = matter(fileContents);

  const processor = await getProcessor();
  const processedContent = await processor.process(content);
  
  const contentHtml = processedContent.toString();

  return {
    slug: decodedSlug,
    content: contentHtml,
    metadata: {
      title: data.title || stripOrderPrefix(path.basename(filePath, ".md")),
      ...data,
    },
  };
}

export function getSidebar(lang: string, type: keyof typeof contentDirectories = "docs"): SidebarItem[] {
  const baseDir = contentDirectories[type];
  const langDir = path.join(baseDir, lang);
  if (!fs.existsSync(langDir)) return [];

  function buildSidebar(dir: string, baseSlug: string[] = []): SidebarItem[] {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    
    const items: SidebarItem[] = entries
      .filter(entry => {
        if (entry.name.startsWith(".")) return false;
        if (entry.name === "index.md") return false;
        if (entry.name === "_meta.json") return false;
        if (entry.name === "public") return false;
        return entry.isDirectory() || entry.name.endsWith(".md");
      })
      .map(entry => {
        const name = entry.name;
        const cleanName = stripOrderPrefix(name).replace(/\.md$/, "");
        const order = getOrder(name);
        const href = `/${lang}/${type}/${[...baseSlug, cleanName].join("/")}`;

        if (entry.isDirectory()) {
          let title = cleanName.charAt(0).toUpperCase() + cleanName.slice(1);
          const metaPath = path.join(dir, name, "_meta.json");
          if (fs.existsSync(metaPath)) {
            try {
              const metaContent = fs.readFileSync(metaPath, "utf8");
              const meta = JSON.parse(metaContent);
              if (meta.title) title = meta.title;
            } catch (e) {
              // Ignore error
            }
          }

          return {
            title,
            href,
            order,
            items: buildSidebar(path.join(dir, name), [...baseSlug, cleanName]),
          };
        }

        const filePath = path.join(dir, name);
        const fileContents = fs.readFileSync(filePath, "utf8");
        const { data } = matter(fileContents);

        return {
          title: data.title || cleanName.charAt(0).toUpperCase() + cleanName.slice(1),
          href,
          order,
        };
      });

    return items.sort((a, b) => a.order - b.order);
  }

  return buildSidebar(langDir);
}
