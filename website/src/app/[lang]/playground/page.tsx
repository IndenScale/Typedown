import { PlaygroundClient } from "./PlaygroundClient";
import { getDictionary } from "@/dictionaries";

export function generateStaticParams() {
  return [{ lang: "en" }, { lang: "zh" }];
}

export default async function PlaygroundPage({
  params,
}: {
  params: Promise<{ lang: string }>;
}) {
  const { lang } = await params;
  const dict = getDictionary(lang);
  return <PlaygroundClient lang={lang} dictionary={dict.playground} />;
}
