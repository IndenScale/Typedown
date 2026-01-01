import { defineConfig } from "vitepress";

export default defineConfig({
  title: "Typedown",
  description: "Progressive Formalization for Markdown",
  cleanUrls: true,
  lang: "zh-CN",

  // Theme Configuration
  themeConfig: {
    siteTitle: "Typedown",
    socialLinks: [
      { icon: "github", link: "https://github.com/indenscale/typedown" },
    ],
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

  ignoreDeadLinks: true,

  vite: {
    server: {
      fs: {
        allow: [".."], // Allow parent directory access if needed
      },
    },
  },
});
