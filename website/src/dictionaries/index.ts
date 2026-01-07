import { en } from "./en";
import { zh } from "./zh";
import { Dictionary } from "./types";

const dictionaries: Record<string, Dictionary> = {
  en,
  zh,
};

export const getDictionary = (lang: string): Dictionary => {
  return dictionaries[lang] || dictionaries.en;
};
