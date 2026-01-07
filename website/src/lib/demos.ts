export type File = {
  name: string;
  language: "typedown" | "python" | "markdown";
  content: string;
  readOnly?: boolean;
  path?: string; // Path to fetch content from (e.g. /demo/laws.td)
};

export type Demo = {
  id: string;
  name: string;
  description: string;
  files: File[];
  activeFileName: string;
};

export const getDemos = (lang: string = "en"): Demo[] => {
  const isZh = lang === "zh";
  const ex = isZh ? "/examples/zh" : "/examples/en";

  return [
    {
      id: "introduction",
      name: isZh ? "00. 项目介绍" : "00. Introduction",
      description: isZh
        ? "了解 Typedown 的核心理念与架构。"
        : "Learn the core concepts and architecture of Typedown.",
      activeFileName: "introduction.md",
      files: [
        {
          name: "introduction.md",
          language: "markdown",
          content: "",
          path: isZh
            ? "/docs/zh/00-introduction.md"
            : "/docs/en/00-introduction.md",
        },
      ],
    },
    {
      id: "quick-start",
      name: isZh ? "01. 快速上手" : "01. Quick Start",
      description: isZh
        ? "编写你的第一个模型与实体。"
        : "Build your first model and entity.",
      activeFileName: "quick-start.md",
      files: [
        {
          name: "quick-start.md",
          language: "markdown",
          content: "",
          path: isZh
            ? "/docs/zh/01-quick-start.md"
            : "/docs/en/01-quick-start.md",
        },
      ],
    },
    {
      id: "00-basic-modeling",
      name: isZh ? "02. 基础建模" : "02. Basic Modeling",
      description: isZh
        ? "Model + Entity 的定义基础。"
        : "The foundation of Model + Entity definition.",
      activeFileName: "intro.td",
      files: [
        {
          name: "README.md",
          language: "markdown",
          content: "",
          path: `${ex}/00_basic_modeling/README.md`,
        },
        {
          name: "intro.td",
          language: "typedown",
          content: "",
          path: `${ex}/00_basic_modeling/intro.td`,
        },
      ],
    },
    {
      id: "01-schema-constraints",
      name: isZh ? "03. Schema 约束" : "03. Schema Constraints",
      description: isZh
        ? "Field + Validator 内置约束。"
        : "Built-in constraints with Field + Validator.",
      activeFileName: "constraints.td",
      files: [
        {
          name: "README.md",
          language: "markdown",
          content: "",
          path: `${ex}/01_schema_constraints/README.md`,
        },
        {
          name: "constraints.td",
          language: "typedown",
          content: "",
          path: `${ex}/01_schema_constraints/constraints.td`,
        },
      ],
    },
    {
      id: "02-inheritance",
      name: isZh ? "04. 模型继承" : "04. Model Inheritance",
      description: isZh ? "复用模型定义。" : "Reuse model definitions.",
      activeFileName: "ebook.td",
      files: [
        {
          name: "README.md",
          language: "markdown",
          content: "",
          path: `${ex}/02_inheritance/README.md`,
        },
        {
          name: "ebook.td",
          language: "typedown",
          content: "",
          path: `${ex}/02_inheritance/ebook.td`,
        },
      ],
    },
    {
      id: "03-simple-rules",
      name: isZh ? "05. 业务规则 (Spec)" : "05. Business Rules (Spec)",
      description: isZh
        ? "使用 Spec 校验业务逻辑。"
        : "Validate business logic using Spec.",
      activeFileName: "rules.td",
      files: [
        {
          name: "README.md",
          language: "markdown",
          content: "",
          path: `${ex}/03_simple_rules/README.md`,
        },
        {
          name: "rules.td",
          language: "typedown",
          content: "",
          path: `${ex}/03_simple_rules/rules.td`,
        },
      ],
    },
    {
      id: "04-context-interaction",
      name: isZh ? "06. 模型方法" : "06. Model Methods",
      description: isZh
        ? "在模型中定义方法。"
        : "Define methods within models.",
      activeFileName: "methods.td",
      files: [
        {
          name: "README.md",
          language: "markdown",
          content: "",
          path: `${ex}/04_context_interaction/README.md`,
        },
        {
          name: "methods.td",
          language: "typedown",
          content: "",
          path: `${ex}/04_context_interaction/methods.td`,
        },
      ],
    },
    {
      id: "05-global-governance",
      name: isZh ? "07. 全局治理" : "07. Global Governance",
      description: isZh
        ? "全局聚合与 SQL 查询。"
        : "Global aggregation and SQL queries.",
      activeFileName: "library.td",
      files: [
        {
          name: "README.md",
          language: "markdown",
          content: "",
          path: `${ex}/05_global_governance/README.md`,
        },
        {
          name: "library.td",
          language: "typedown",
          content: "",
          path: `${ex}/05_global_governance/library.td`,
        },
      ],
    },
    {
      id: "06-modular-project",
      name: isZh ? "08. 模块化项目" : "08. Modular Project",
      description: isZh
        ? "多文件组织与配置。"
        : "Multi-file organization and configuration.",
      activeFileName: "data.td",
      files: [
        {
          name: "README.md",
          language: "markdown",
          content: "",
          path: `${ex}/06_modular_project/README.md`,
        },
        {
          name: "config.td",
          language: "typedown",
          content: "",
          path: `${ex}/06_modular_project/config.td`,
        },
        {
          name: "models.td",
          language: "typedown",
          content: "",
          path: `${ex}/06_modular_project/models.td`,
        },
        {
          name: "data.td",
          language: "typedown",
          content: "",
          path: `${ex}/06_modular_project/data.td`,
        },
      ],
    },
    {
      id: "one-king",
      name: isZh ? "经典：Only One King" : "Classic: Only One King",
      description: isZh
        ? "演示复杂逻辑约束的经典案例。"
        : "A classic case demonstrating complex logic constraints.",
      activeFileName: "laws.td",
      files: [
        {
          name: "laws.td",
          language: "typedown",
          content: "",
          path: `${ex}/laws.td`,
        },
      ],
    },
  ];
};

// Legacy compatibility - defaults to 'en'
export const DEMOS = getDemos("en");
