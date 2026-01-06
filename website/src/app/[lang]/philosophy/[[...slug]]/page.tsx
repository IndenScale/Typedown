import React from "react";
import { getDocBySlug, getSidebar, getAllDocs } from "@/lib/docs";
import { notFound, redirect } from "next/navigation";

interface PageProps {
  params: Promise<{
    lang: string;
    slug?: string[];
  }>;
}

export async function generateStaticParams() {
  const allParams = [];
  const langs = ["en", "zh"];

  for (const lang of langs) {
    // Add the root philosophy page for each language
    allParams.push({ lang, slug: [] });

    const docs = getAllDocs(lang, "philosophy");
    for (const doc of docs) {
      // Remove the lang prefix from slug as it's handled by [lang] param
      const slug = doc.slug.slice(1);
      allParams.push({ lang, slug });
    }
  }

  return allParams;
}

export default async function PhilosophyPage({ params }: PageProps) {
  const { lang, slug = [] } = await params;

  // If slug is empty, we are at /philosophy/[lang], redirect to the first item
  if (slug.length === 0) {
    const sidebar = getSidebar(lang, "philosophy");
    if (sidebar.length > 0) {
      let firstItem = sidebar[0];
      if (firstItem.items && firstItem.items.length > 0) {
        firstItem = firstItem.items[0];
      }
      redirect(encodeURI(firstItem.href));
    } else {
      notFound();
    }
  }

  const docSlug = [lang, ...slug];
  const doc = await getDocBySlug(docSlug, "philosophy");

  if (!doc) {
    notFound();
  }

  return (
    <article className="prose prose-slate dark:prose-invert max-w-none">
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
