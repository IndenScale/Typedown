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

export const DEMOS: Demo[] = [
  {
    id: "one-king",
    name: "Only One King",
    description:
      "A classic example demonstrating logic constraints in Typedown.",
    activeFileName: "laws.td",
    files: [
      {
        name: "laws.td",
        language: "typedown",
        content: "", // Will be fetched
        path: "/demo/laws.td",
      },
    ],
  },
];
