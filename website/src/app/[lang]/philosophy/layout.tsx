import React from "react";
import { getSidebar } from "@/lib/docs";
import Link from "next/link";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";

export default async function PhilosophyLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ lang: string }>;
}) {
  const { lang } = await params;
  const sidebar = getSidebar(lang, "philosophy");

  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <div className="flex flex-1 justify-center">
        <div className="flex w-full max-w-[90rem] px-6">
          <aside className="hidden w-64 flex-shrink-0 border-r border-black/5 dark:border-white/5 py-10 sm:block">
            <nav className="sticky top-24 space-y-8">
              {sidebar.map((section) => (
                <div key={section.href}>
                  {section.items ? (
                    <>
                      <h5 className="mb-3 text-sm font-semibold text-foreground">
                        {section.title}
                      </h5>
                      <ul className="space-y-2 border-l border-black/5 dark:border-white/5 ml-1">
                        {section.items.map((item) => (
                          <li key={item.href}>
                            <Link
                              href={item.href}
                              className="block pl-4 text-sm text-gray-500 hover:text-foreground transition-colors"
                            >
                              {item.title}
                            </Link>
                          </li>
                        ))}
                      </ul>
                    </>
                  ) : (
                    <Link
                      href={section.href}
                      className="block text-sm font-semibold text-gray-500 hover:text-foreground transition-colors"
                    >
                      {section.title}
                    </Link>
                  )}
                </div>
              ))}
            </nav>
          </aside>
          <main className="flex-1 py-10 pl-0 sm:pl-10 min-w-0">
            {children}
          </main>
        </div>
      </div>
      <Footer />
    </div>
  );
}
