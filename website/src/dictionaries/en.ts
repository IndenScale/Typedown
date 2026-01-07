import { Dictionary } from "./types";

export const en: Dictionary = {
  common: {
    language: "English",
    theme: {
      toggle: "Toggle theme",
    },
  },
  nav: {
    philosophy: "Philosophy",
    docs: "Docs",
    playground: "Playground",
  },
  footer: {
    tagline: "Markdown that catches errors.",
    subTagline: "Before your team does.",
    product: "Product",
    company: "Company",
    docs: "Documentation",
    manifesto: "Manifesto",
    contact: "Contact",
    copyright: "Monoco. Built for Elite Developers and AI Agents.",
  },
  home: {
    hero: {
      title_start: "Markdown that ",
      title_highlight: "scales",
      title_end: ".",
      description_start:
        "Build trusted knowledge bases with Markdown, Pydantic, and Pytest.",
      description_highlight: "",
      description_end:
        "The rigor of code meets the fluidity of natural language.",
      installBtn: "Install Extension",
      playgroundBtn: "Try Playground",
      openVsx: "Also available on Open VSX",
    },
    features: {
      schema: {
        title: "Schema-First",
        desc_start: "Define the structure of your knowledge base using",
        desc_highlight: " Pydantic",
        desc_end: " models. No more unstructured chaos.",
      },
      logic: {
        title: "Logic Constraints",
        desc_start: "Write validation rules in pure",
        desc_highlight: " Python",
        desc_end: ". If the logic holds in code, it holds in reality.",
      },
      feedback: {
        title: "Instant Feedback",
        desc_start: "Catch logical contradictions and data errors",
        desc_highlight: " directly in the editor",
        desc_end: ", just like a compiler for your notes.",
      },
    },
    showcase: {
      exploreMore: "Explore more examples in Playground",
      or: "or",
      readDocs: "Read syntax documentation",
      marker_error:
        "Spec Error: The land cannot sustain two crowns! (Triggered by test_there_can_be_only_one)",
    },
    ai: {
      title_start: "Built for the ",
      title_highlight: "AI Era",
      title_end: ".",
      desc: "Typedown isn't just for humans. We provide pre-built Skills that teach AI Agents how to read, write, and validate Typedown documents.",
      enableTitle: "How to enable AI Skills",
      step1: {
        title: "Create and Place Skills",
        desc_pre: "Create ",
        desc_code: "skills/typedown-expert",
        desc_post:
          " directory in your project root, and download skill.md into it.",
      },
      downloadBtn: "Download skill.md",
      step2: {
        title: "Update System Prompt",
        desc_pre: "Add instructions to your ",
        desc_code: "Agents.md",
        desc_post: " or system prompt to let the AI discover the skill:",
      },
      prompt:
        "Read the content in ./skills to understand how to interact with Typedown files.",
    },
  },
  playground: {
    header: {
      title: "PLAYGROUND",
      demo: "Demo:",
    },
    explorer: {
      title: "Explorer",
    },
    editor: {
      noFileOpen: "No file is open.",
      selectFile: "Select a file from the explorer to start editing.",
    },
  },
};
