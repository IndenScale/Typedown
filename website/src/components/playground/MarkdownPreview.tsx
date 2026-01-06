"use client";

import { useEffect, useState } from "react";
import { remark } from "remark";
import html from "remark-html";

interface MarkdownPreviewProps {
  content: string;
}

export function MarkdownPreview({ content }: MarkdownPreviewProps) {
  const [htmlContent, setHtmlContent] = useState("");

  useEffect(() => {
    // Process markdown to HTML
    // We use a simple pipeline here for the browser
    remark()
      .use(html)
      .process(content)
      .then((file) => {
        setHtmlContent(String(file));
      })
      .catch((err) => {
        console.error("Markdown processing error:", err);
        setHtmlContent(`<p style="color:red">Error rendering markdown</p>`);
      });
  }, [content]);

  return (
    <div className="h-full w-full overflow-y-auto bg-white dark:bg-[#0A0A0A] p-6">
      <div
        className="markdown-content max-w-4xl mx-auto pb-20"
        dangerouslySetInnerHTML={{ __html: htmlContent }}
      />
    </div>
  );
}
