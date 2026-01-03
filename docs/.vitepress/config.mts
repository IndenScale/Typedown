import { defineConfig } from "vitepress";

export default defineConfig({
  title: "Typedown",
  description: "Progressive Formalization for Markdown",
  cleanUrls: true,

  // Shared ignore
  ignoreDeadLinks: true,

  head: [
    [
      "link",
      {
        rel: "icon",
        href: "/assets/brand/icon-light.svg",
        media: "(prefers-color-scheme: light)",
      },
    ],
    [
      "link",
      {
        rel: "icon",
        href: "/assets/brand/icon-dark.svg",
        media: "(prefers-color-scheme: dark)",
      },
    ],
  ],
  themeConfig: {
    logo: {
      light: "/assets/brand/logo-light.svg",
      dark: "/assets/brand/logo-dark.svg",
    },
    socialLinks: [
      { icon: "github", link: "https://github.com/indenscale/typedown" },
    ],
  },

  locales: {
    root: {
      label: "English",
      lang: "en",
      link: "/en/", // We are using explicit /en/ prefix for consistency
      title: "Typedown",
      description: "Progressive Formalization for Markdown",
      themeConfig: {
        nav: [
          { text: "Manifesto", link: "/en/manifesto" },
          { text: "Core Concepts", link: "/en/00-core-concepts" },
          { text: "Tutorial", link: "/en/tutorial" },
        ],
        sidebar: [
          {
            text: "Philosophy",
            items: [
              { text: "Manifesto", link: "/en/manifesto" },
              { text: "Core Concepts", link: "/en/00-core-concepts" },
            ],
          },
          {
            text: "Syntax",
            items: [
              { text: "Code Blocks", link: "/en/01-syntax/01-code-blocks" },
              { text: "References", link: "/en/01-syntax/02-references" },
              { text: "Identifiers", link: "/en/01-syntax/03-identifiers" },
            ],
          },
          {
            text: "Semantics",
            items: [
              { text: "Evolution", link: "/en/02-semantics/01-evolution" },
              {
                text: "Context & Scoping",
                link: "/en/02-semantics/02-context-scoping",
              },
            ],
          },
          {
            text: "Runtime",
            items: [
              { text: "Script System", link: "/en/03-runtime/01-scripting" },
              {
                text: "Quality Control",
                link: "/en/03-runtime/02-quality-control",
              },
              {
                text: "LSP Architecture",
                link: "/en/03-runtime/03-lsp-architecture",
              },
            ],
          },
          {
            text: "Best Practices",
            items: [
              {
                text: "Identity Management",
                link: "/en/04-best-practices/01-identity-mgmt",
              },
            ],
          },
          {
            text: "Getting Started",
            items: [{ text: "Tutorial", link: "/en/tutorial" }],
          },
        ],
        docFooter: { prev: "Previous", next: "Next" },
        outline: { label: "On this page" },
        returnToTopLabel: "Return to top",
        sidebarMenuLabel: "Menu",
        darkModeSwitchLabel: "Dark Mode",
      },
    },
    zh: {
      label: "简体中文",
      lang: "zh-CN",
      link: "/zh/",
      title: "Typedown",
      description: "渐进式形式化",
      themeConfig: {
        nav: [
          { text: "宣言", link: "/zh/manifesto" },
          { text: "核心理念", link: "/zh/00-核心理念" },
          { text: "技术规范", link: "/zh/01-语法/01-代码块" },
        ],
        sidebar: [
          {
            text: "理念",
            items: [
              { text: "宣言", link: "/zh/manifesto" },
              { text: "核心理念", link: "/zh/00-核心理念" },
            ],
          },
          {
            text: "语法 (Syntax)",
            items: [
              { text: "代码块", link: "/zh/01-语法/01-代码块" },
              { text: "引用", link: "/zh/01-语法/02-引用" },
              { text: "标识符", link: "/zh/01-语法/03-标识符" },
            ],
          },
          {
            text: "语义 (Semantics)",
            items: [
              { text: "演变语义", link: "/zh/02-语义/01-演变语义" },
              {
                text: "上下文与作用域",
                link: "/zh/02-语义/02-上下文与作用域",
              },
            ],
          },
          {
            text: "运行 (Runtime)",
            items: [
              { text: "脚本系统", link: "/zh/03-运行/01-脚本系统" },
              { text: "质量控制", link: "/zh/03-运行/02-质量控制" },
              { text: "LSP架构", link: "/zh/03-运行/03-LSP架构" },
            ],
          },
          {
            text: "最佳实践",
            items: [{ text: "身份管理", link: "/zh/04-最佳实践/01-身份管理" }],
          },
        ],
        docFooter: {
          prev: "上一页",
          next: "下一页",
        },
        outline: {
          label: "页面导航",
        },
        returnToTopLabel: "回到顶部",
        sidebarMenuLabel: "菜单",
        darkModeSwitchLabel: "深色模式",
      },
    },
  },

  vite: {
    server: {
      fs: {
        allow: [".."], // Allow parent directory access if needed
      },
    },
  },
});
