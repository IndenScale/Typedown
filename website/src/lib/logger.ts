const LOG_LEVELS = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3,
};

type LogLevel = keyof typeof LOG_LEVELS;

class Logger {
  private level: LogLevel = "info";
  private prefix: string = "[Typedown]";

  constructor() {
    // Check for debug flag in localStorage or URL params if in browser
    if (typeof window !== "undefined") {
      const searchParams = new URLSearchParams(window.location.search);
      if (
        searchParams.has("debug") ||
        localStorage.getItem("typedown_debug") === "true"
      ) {
        this.level = "debug";
      } else if (process.env.NODE_ENV === "development") {
        this.level = "debug";
      }
    }
  }

  private shouldLog(level: LogLevel): boolean {
    return LOG_LEVELS[level] >= LOG_LEVELS[this.level];
  }

  private formatMessage(message: string): string {
    return `${this.prefix} ${message}`;
  }

  debug(message: string, ...args: unknown[]) {
    if (this.shouldLog("debug")) {
      console.debug(this.formatMessage(message), ...args);
    }
  }

  info(message: string, ...args: unknown[]) {
    if (this.shouldLog("info")) {
      console.info(this.formatMessage(message), ...args);
    }
  }

  warn(message: string, ...args: unknown[]) {
    if (this.shouldLog("warn")) {
      console.warn(this.formatMessage(message), ...args);
    }
  }

  error(message: string, ...args: unknown[]) {
    if (this.shouldLog("error")) {
      console.error(this.formatMessage(message), ...args);
    }
  }
}

export const logger = new Logger();
