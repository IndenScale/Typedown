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
    ]
  },

  ignoreDeadLinks: true,

  vite: {
    server: {
      fs: {
        allow: [".."],
      },
    },
  },

  locales: {
    root: {
      label: 'English',
      lang: 'en',
      themeConfig: {
        nav: [
          { text: 'Manifesto', link: '/docs/manifesto' },
          { text: 'Guide', link: '/docs/guide/01_syntax' },
          { text: 'Reference', link: '/docs/reference/cli' }
        ],
        sidebar: {
          '/docs/guide/': [
            {
              text: 'User Guide',
              items: [
                { text: '1. Syntax Guide', link: '/docs/guide/01_syntax' },
                { text: '2. Testing & Validation', link: '/docs/guide/02_testing' },
                { text: '3. Project Structure', link: '/docs/guide/03_project_structure' }
              ]
            }
          ],
          '/docs/reference/': [
            {
              text: 'Reference',
              items: [
                { text: 'CLI Reference', link: '/docs/reference/cli' },
                { text: 'Architecture', link: '/docs/reference/architecture' }
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
          { text: '宣言', link: '/docs/zh/manifesto' },
          { text: '指南', link: '/docs/zh/guide/01_syntax' },
          { text: '参考', link: '/docs/zh/reference/cli' }
        ],
        sidebar: {
          '/docs/zh/guide/': [
            {
              text: '用户指南',
              items: [
                { text: '1. 语法指南', link: '/docs/zh/guide/01_syntax' },
                { text: '2. 测试与验证', link: '/docs/zh/guide/02_testing' },
                { text: '3. 项目结构', link: '/docs/zh/guide/03_project_structure' }
              ]
            }
          ],
          '/docs/zh/reference/': [
            {
              text: '参考手册',
              items: [
                { text: 'CLI 参考', link: '/docs/zh/reference/cli' },
                { text: '架构', link: '/docs/zh/reference/architecture' }
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