export interface Dictionary {
  common: {
    language: string;
    theme: {
      toggle: string;
    };
  };
  nav: {
    philosophy: string;
    docs: string;
    playground: string;
  };
  footer: {
    tagline: string;
    subTagline: string;
    product: string;
    company: string;
    docs: string;
    manifesto: string;
    contact: string;
    copyright: string;
  };
  home: {
    hero: {
      title_start: string;
      title_highlight: string;
      title_end: string;
      description_start: string;
      description_highlight: string;
      description_end: string;
      installBtn: string;
      playgroundBtn: string;
      openVsx: string;
    };
    features: {
      schema: {
        title: string;
        desc_start: string;
        desc_highlight: string;
        desc_end: string;
      };
      logic: {
        title: string;
        desc_start: string;
        desc_highlight: string;
        desc_end: string;
      };
      feedback: {
        title: string;
        desc_start: string;
        desc_highlight: string;
        desc_end: string;
      };
    };
    showcase: {
      exploreMore: string;
      or: string;
      readDocs: string;
      marker_error: string;
    };
    ai: {
      title_start: string;
      title_highlight: string;
      title_end: string;
      desc: string;
      enableTitle: string;
      step1: {
        title: string;
        desc_pre: string;
        desc_code: string;
        desc_post: string;
      };
      downloadBtn: string;
      step2: {
        title: string;
        desc_pre: string;
        desc_code: string;
        desc_post: string;
      };
      prompt: string;
    };
  };
  playground: {
    header: {
      title: string;
      demo: string;
    };
    explorer: {
      title: string;
    };
    editor: {
      noFileOpen: string;
      selectFile: string;
    };
  };
}
