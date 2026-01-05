import React from "react";
import { getDocBySlug, getSidebar } from "@/lib/docs";
import { notFound, redirect } from "next/navigation";
import { MermaidInitializer } from "@/components/MermaidInitializer";

interface PageProps {
  params: Promise<{
    lang: string;
    slug?: string[];
  }>;
}

export default async function DocPage({ params }: PageProps) {
  const { lang, slug = [] } = await params;
  
  // If slug is empty, we are at /docs/[lang], redirect to the first doc
  if (slug.length === 0) {
    const sidebar = getSidebar(lang);
    if (sidebar.length > 0) {
      // Find the first item (could be a nested item)
      let firstItem = sidebar[0];
      if (firstItem.items && firstItem.items.length > 0) {
        firstItem = firstItem.items[0];
      }
      // Ensure the URL is properly encoded to avoid "Invalid character in header content" error
      // when the URL contains non-ASCII characters (e.g. Chinese filenames).
      redirect(encodeURI(firstItem.href));
    } else {
      notFound();
    }
  }

  const docSlug = [lang, ...slug];
  const doc = await getDocBySlug(docSlug);

  if (!doc) {
    notFound();
  }

  return (
    <article className="prose prose-slate dark:prose-invert max-w-none">
      <MermaidInitializer />
      <header className="mb-10">
        <h1 className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
          {doc.metadata.title}
        </h1>
      </header>
      <div 
        className="markdown-content"
        dangerouslySetInnerHTML={{ __html: doc.content }} 
      />
    </article>
  );
}
