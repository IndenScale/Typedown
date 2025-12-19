import { defineConfig } from 'vitepress'

export default defineConfig({
  title: "Typedown",
  description: "Progressive Formalization for Markdown",
  cleanUrls: true,

  // Shared Theme Configuration
  themeConfig: {
    logo: { text: "Typedown" },
    siteTitle: "Typedown",
    socialLinks: [
      { icon: 'github', link: 'https://github.com/indenscale/typedown' }
    ],
    localeLinks: {
      text: 'Language',
      items: [
        { text: 'English', link: '/' },
        { text: '简体中文', link: '/zh/' }
      ]
    }
  },

  ignoreDeadLinks: true,

  vite: {
    server: {
      fs: {
        allow: [".."], // Allow parent directory access if needed
      },
    },
  },

  locales: {
    root: {
      label: 'English',
      lang: 'en',
      themeConfig: {
        nav: [
          { text: 'Manifesto', link: '/manifesto' },
          { text: 'Guide', link: '/guide/01_syntax' },
          { text: 'Reference', link: '/reference/cli' }
        ],
        sidebar: {
          '/guide/': [
            {
              text: 'User Guide',
              items: [
                { text: '1. Syntax Guide', link: '/guide/01_syntax' },
                { text: '2. Testing & Validation', link: '/guide/02_testing' },
                { text: '3. Project Structure', link: '/guide/03_project_structure' }
              ]
            }
          ],
          '/reference/': [
            {
              text: 'Reference',
              items: [
                { text: 'CLI Reference', link: '/reference/cli' },
                { text: 'Architecture', link: '/reference/architecture' }
              ]
            }
          ]
        }
      }
    },
    zh: {
      label: '简体中文',
      lang: 'zh',
      link: '/zh/',
      themeConfig: {
        nav: [
          { text: '宣言', link: '/zh/manifesto' },
          { text: '指南', link: '/zh/guide/01_syntax' },
          { text: '参考', link: '/zh/reference/cli' }
        ],
        sidebar: {
          '/zh/guide/': [
            {
              text: '用户指南',
              items: [
                { text: '1. 语法指南', link: '/zh/guide/01_syntax' },
                { text: '2. 测试与验证', link: '/zh/guide/02_testing' },
                { text: '3. 项目结构', link: '/zh/guide/03_project_structure' }
              ]
            }
          ],
          '/zh/reference/': [
            {
              text: '参考手册',
              items: [
                { text: 'CLI 参考', link: '/zh/reference/cli' },
                { text: '架构', link: '/zh/reference/architecture' }
              ]
            }
          ]
        },
        docFooter: {
          prev: '上一页',
          next: '下一页'
        },
        outline: {
          label: '页面导航'
        },
        returnToTopLabel: '回到顶部',
        sidebarMenuLabel: '菜单',
        darkModeSwitchLabel: '深色模式'
      }
    }
  }
})