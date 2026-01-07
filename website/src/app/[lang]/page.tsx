import { LandingCodeEditor } from "@/components/landing/LandingCodeEditor";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import Link from "next/link";
import { getDictionary } from "@/dictionaries";

export function generateStaticParams() {
  return [{ lang: "en" }, { lang: "zh" }];
}

export default async function Home({
  params,
}: {
  params: Promise<{ lang: string }>;
}) {
  const { lang } = await params;
  const dict = getDictionary(lang);
  const isZh = lang === "zh";

  const hero = dict.home.hero;
  const features = dict.home.features;
  const showcase = dict.home.showcase;
  const ai = dict.home.ai;

  const content = {
    title: (
      <>
        {hero.title_start}
        <span className="text-success underline decoration-success/30 underline-offset-8">
          {hero.title_highlight}
        </span>
        {hero.title_end}
      </>
    ),
    description: (
      <>
        {hero.description_start}
        {hero.description_highlight && (
          <span className="text-success"> {hero.description_highlight}</span>
        )}
        {hero.description_end && <br />}
        {hero.description_end}
      </>
    ),
    installBtn: hero.installBtn,
    playgroundBtn: hero.playgroundBtn,
    openVsx: hero.openVsx,
    features: [
      {
        title: features.schema.title,
        description: (
          <>
            {features.schema.desc_start}
            <span className="text-success">
              {features.schema.desc_highlight}
            </span>
            {features.schema.desc_end}
          </>
        ),
      },
      {
        title: features.logic.title,
        description: (
          <>
            {features.logic.desc_start}
            <span className="text-success">
              {features.logic.desc_highlight}
            </span>
            {features.logic.desc_end}
          </>
        ),
      },
      {
        title: features.feedback.title,
        description: (
          <>
            {features.feedback.desc_start}
            <span className="text-success">
              {features.feedback.desc_highlight}
            </span>
            {features.feedback.desc_end}
          </>
        ),
      },
    ],
    exploreMore: showcase.exploreMore,
    or: showcase.or,
    readDocs: showcase.readDocs,
    aiTitle: (
      <>
        {ai.title_start}
        <span className="text-success">{ai.title_highlight}</span>
        {ai.title_end}
      </>
    ),
    aiDesc: ai.desc,
    aiEnableTitle: ai.enableTitle,
    aiStep1Title: ai.step1.title,
    aiStep1Desc: (
      <>
        {ai.step1.desc_pre}
        <code className="px-1.5 py-0.5 rounded bg-black/5 dark:bg-white/10 font-mono text-xs">
          {ai.step1.desc_code}
        </code>
        {ai.step1.desc_post}
      </>
    ),
    aiDownloadBtn: ai.downloadBtn,
    aiStep2Title: ai.step2.title,
    aiStep2Desc: (
      <>
        {ai.step2.desc_pre}
        <code className="px-1.5 py-0.5 rounded bg-black/5 dark:bg-white/10 font-mono text-xs">
          {ai.step2.desc_code}
        </code>
        {ai.step2.desc_post}
      </>
    ),
    aiPrompt: ai.prompt,
    aiSkillUrl: "/api/download-skill",
  };

  const kingCode = isZh
    ? `# 王国的法律

## 1. 皇家类 (Schema)
首先，我们为领域定义数据结构。

\`\`\`model:Character
class Character(BaseModel):
    name: str
\`\`\`

\`\`\`model:King
class King(Character):
    # King 类继承自 Character
    pass
\`\`\`

## 2. 唯一性约束 (Spec)
接着，我们定义规则。此 spec 确保只有一个国王存在。

\`\`\`spec:uniqueness_check
def test_there_can_be_only_one(entities):
    # 查询所有 King 的实例
    kings = [e for e in entities if isinstance(e, King)]
    
    # 断言数量最多为 1
    if len(kings) > 1:
        raise ValueError("这片土地无法承载两顶王冠！")
\`\`\`

## 3. 冲突 (Data)
最后，我们尝试创建两个国王，触发错误。

entity King: arthur
  name: "亚瑟·潘德拉贡"

entity King: mordred
  name: "篡位者莫德雷德"`
    : `# The Laws of the Kingdom

## 1. The Royal Class (Schema)
First, we define the data structure for our domain.

\`\`\`model:Character
class Character(BaseModel):
    name: str
\`\`\`

\`\`\`model:King
class King(Character):
    # The King class inherits from Character
    pass
\`\`\`

## 2. The Uniqueness Constraint (Spec)
Then, we define the rules. This spec ensures only one King exists.

\`\`\`spec:uniqueness_check
def test_there_can_be_only_one(entities):
    # Query all entities that are instances of King
    kings = [e for e in entities if isinstance(e, King)]
    
    # Assert that the count is at most 1
    if len(kings) > 1:
        raise ValueError("The land cannot sustain two crowns!")
\`\`\`

## 3. The Conflict (Data)
Finally, we try to create two Kings, triggering the error.

entity King: arthur
  name: "Arthur Pendragon"

entity King: mordred
  name: "Mordred the Pretender"`;

  // Simulate LSP logic to find the conflict block dynamically
  const getConflictDiagnostics = (code: string) => {
    const lines = code.split("\n");
    const startLineIndex = lines.findIndex((line) =>
      line.includes("entity King: mordred")
    );

    if (startLineIndex === -1) return [];

    // Find the end of the block (simple heuristic: look for next empty line or end of string)
    let endLineIndex = startLineIndex;
    while (
      endLineIndex + 1 < lines.length &&
      lines[endLineIndex + 1].trim() !== ""
    ) {
      endLineIndex++;
    }

    const lastLine = lines[endLineIndex];

    return [
      {
        startLineNumber: startLineIndex + 1,
        startColumn: 1,
        endLineNumber: endLineIndex + 1,
        endColumn: lastLine.length + 1,
        message: isZh
          ? "Spec Error: 这片土地无法承载两顶王冠！ (由 test_there_can_be_only_one 触发)"
          : "Spec Error: The land cannot sustain two crowns! (Triggered by test_there_can_be_only_one)",
        severity: 8,
      },
    ];
  };

  const markers = getConflictDiagnostics(kingCode);

  return (
    <div className="flex min-h-screen flex-col items-center selection:bg-success selection:text-black">
      <Header nav={dict.nav} />

      {/* Ghost Blue Accent Light Leak */}
      <div className="fixed top-0 left-1/2 -z-10 h-[500px] w-[800px] -translate-x-1/2 rounded-full bg-ghost-blue blur-[120px] pointer-events-none opacity-50 dark:opacity-100" />

      {/* Hero Section */}
      <main className="flex w-full max-w-7xl flex-col items-center px-6 pt-20 pb-32 text-center sm:pt-32">
        <h1 className="text-5xl font-bold tracking-tight sm:text-7xl">
          {content.title}
        </h1>
        <p className="mt-8 max-w-2xl text-lg text-gray-400 sm:text-xl leading-relaxed">
          {content.description}
        </p>

        <div className="mt-12 flex flex-col items-center gap-6">
          <div className="flex items-center justify-center gap-4">
            <a
              href="https://marketplace.visualstudio.com/items?itemName=Typedown.typedown-vscode-integration"
              target="_blank"
              rel="noopener noreferrer"
              className="flex h-12 w-48 items-center justify-center rounded-lg bg-foreground px-4 font-medium text-background transition-all duration-200 hover:opacity-90 hover:shadow-lg active:scale-[0.97] active:opacity-100">
              {content.installBtn}
            </a>
            <Link
              href={`/${lang}/playground`}
              className="flex h-12 w-48 items-center justify-center rounded-lg border border-black/10 dark:border-white/10 bg-transparent px-4 font-medium text-foreground transition-all duration-200 hover:bg-black/5 dark:hover:bg-white/5 hover:border-black/20 dark:hover:border-white/20 active:scale-[0.97] active:bg-black/[0.08] dark:active:bg-white/[0.08]">
              {content.playgroundBtn}
            </Link>
          </div>
          <a
            href="https://open-vsx.org/extension/Typedown/typedown-vscode-integration"
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-gray-500 hover:text-foreground transition-colors">
            {content.openVsx}
          </a>
        </div>

        {/* Feature Grid - Inspired by TS Site "Safety at Scale" */}
        <div className="mt-24 grid w-full max-w-5xl grid-cols-1 gap-12 sm:grid-cols-3 text-left">
          {content.features.map((feature, index) => (
            <div key={index} className="space-y-4">
              <h3 className="text-xl font-bold text-foreground">
                {feature.title}
              </h3>
              <p className="text-gray-400 leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>

        {/* The "TS-Style" Editor Showcase */}
        <div className="mt-24 w-full max-w-6xl">
          <LandingCodeEditor
            fileName="world/laws.td"
            code={kingCode}
            markers={markers}
            autoHeight={true}
          />
          <div className="mt-10 flex flex-col items-center gap-4">
            <Link
              href={`/${lang}/playground`}
              className="group flex items-center gap-2 text-lg font-medium text-success transition-all hover:text-success/80">
              {content.exploreMore}
              <span className="transition-transform group-hover:translate-x-1">
                →
              </span>
            </Link>
            <div className="flex items-center gap-3 text-sm text-gray-500">
              <span>{content.or}</span>
              <Link
                href={`/${lang}/docs`}
                className="hover:text-foreground transition-colors border-b border-gray-500/30 hover:border-foreground/30 pb-0.5">
                {content.readDocs}
              </Link>
            </div>
          </div>
        </div>

        {/* AI Skills Section */}
        <div className="mt-32 w-full max-w-4xl border-t border-black/10 dark:border-white/10 pt-24">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            {content.aiTitle}
          </h2>
          <p className="mt-6 text-lg text-gray-400 leading-relaxed">
            {content.aiDesc}
          </p>

          <div className="mt-10 rounded-xl border border-black/10 bg-gray-50/50 p-6 dark:border-white/10 dark:bg-white/5 text-left">
            <h4 className="font-mono text-sm font-bold text-gray-500 uppercase tracking-wider mb-4">
              {content.aiEnableTitle}
            </h4>
            <div className="space-y-4">
              <div className="flex gap-4">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-success/10 text-success font-bold text-sm">
                  1
                </div>
                <div className="flex-1">
                  <p className="font-medium">{content.aiStep1Title}</p>
                  <p className="text-sm text-gray-500 mt-1">
                    {content.aiStep1Desc}
                  </p>
                  <a
                    href={content.aiSkillUrl}
                    download="skill.md"
                    className="mt-3 inline-flex items-center gap-2 rounded-md bg-success/10 px-3 py-1.5 text-xs font-semibold text-success transition-all hover:bg-success/20 active:scale-95">
                    <svg
                      width="14"
                      height="14"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v4" />
                      <polyline points="7 10 12 15 17 10" />
                      <line x1="12" y1="15" x2="12" y2="3" />
                    </svg>
                    {content.aiDownloadBtn}
                  </a>
                </div>
              </div>
              <div className="flex gap-4">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-success/10 text-success font-bold text-sm">
                  2
                </div>
                <div>
                  <p className="font-medium">{content.aiStep2Title}</p>
                  <p className="text-sm text-gray-500 mt-1">
                    {content.aiStep2Desc}
                  </p>
                  <div className="mt-3 rounded-md bg-black/5 dark:bg-black/40 p-3 font-mono text-xs text-gray-600 dark:text-gray-400">
                    &quot;{content.aiPrompt}&quot;
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      <Footer content={dict.footer} />
    </div>
  );
}
