import { PlaygroundClient } from "./PlaygroundClient";

export function generateStaticParams() {
  return [{ lang: "en" }, { lang: "zh" }];
}

export default async function PlaygroundPage({
  params,
}: {
  params: Promise<{ lang: string }>;
}) {
  const { lang } = await params;
  return <PlaygroundClient lang={lang} />;
}
