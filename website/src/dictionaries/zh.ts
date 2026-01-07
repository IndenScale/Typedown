import { Dictionary } from "./types";

export const zh: Dictionary = {
  common: {
    language: "简体中文",
    theme: {
      toggle: "切换主题",
    },
  },
  nav: {
    philosophy: "理念",
    docs: "文档",
    playground: "Playground",
  },
  footer: {
    tagline: "Markdown 的自由，代码级的严谨。",
    subTagline: "面向 AI 协作的知识建模语言。",
    product: "产品",
    company: "关于",
    docs: "文档",
    manifesto: "宣言",
    contact: "联系我们",
    copyright: "Monoco. 为精英开发者与 AI Agent 打造。",
  },
  home: {
    hero: {
      title_start: "编写 Markdown 拥有",
      title_highlight: "规模化",
      title_end: "的能力。",
      description_start: "基于 Markdown、Pydantic 和 Pytest 构建可信知识库。",
      description_highlight: "",
      description_end: "代码的严谨性与自然语言的流动性在此共生。",
      installBtn: "安装扩展",
      playgroundBtn: "尝试 Playground",
      openVsx: "也可在 Open VSX 获取",
    },
    features: {
      schema: {
        title: "结构先行 (Schema-First)",
        desc_start: "使用 ",
        desc_highlight: "Pydantic",
        desc_end: " 模型定义知识库结构。终结无序的文档混乱。",
      },
      logic: {
        title: "逻辑约束",
        desc_start: "使用原生 ",
        desc_highlight: "Python",
        desc_end: " 编写校验规则。只要逻辑在代码中成立，它在现实中就成立。",
      },
      feedback: {
        title: "即时反馈",
        desc_start: "直接在 ",
        desc_highlight: "编辑器中",
        desc_end: " 捕获逻辑矛盾和数据错误，就像为你的笔记配备了编译器。",
      },
    },
    showcase: {
      exploreMore: "在 Playground 中探索更多示例",
      or: "或",
      readDocs: "阅读语法文档",
      marker_error:
        "Spec Error: 这片土地无法承载两顶王冠！ (由 test_there_can_be_only_one 触发)",
    },
    ai: {
      title_start: "为 ",
      title_highlight: "AI 时代",
      title_end: " 而生。",
      desc: "Typedown 不仅仅是为人类设计的。我们提供预置的 Skills，教导 AI Agent 如何阅读、编写和校验 Typedown 文档。",
      enableTitle: "如何启用 AI Skills",
      step1: {
        title: "创建并放置 Skills",
        desc_pre: "在项目根目录创建 ",
        desc_code: "skills/typedown-expert",
        desc_post: " 目录，并下载 skill.md 放入其中。",
      },
      downloadBtn: "下载 skill.md",
      step2: {
        title: "更新系统提示词 (System Prompt)",
        desc_pre: "在你的 ",
        desc_code: "Agents.md",
        desc_post: " 或系统指令中添加指引，让 AI 发现该技能：",
      },
      prompt: "阅读 ./skills 中的内容，了解如何与 Typedown 文件交互。",
    },
  },
  playground: {
    header: {
      title: "PLAYGROUND",
      demo: "示例:",
    },
    explorer: {
      title: "资源管理器",
    },
    editor: {
      noFileOpen: "未打开文件",
      selectFile: "从资源管理器中选择一个文件开始编辑。",
    },
  },
};
