import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // 1. Static Asset Detection (Robust)
  // Logic: If it has a file extension (contains ".") OR starts with /api, we skip redirection.
  // This automatically handles .whl, .png, .wasm, etc. without manual maintenance.
  if (
    pathname.includes(".") ||
    pathname.startsWith("/api") ||
    pathname.startsWith("/_next")
  ) {
    return;
  }

  // 2. Locale Prefix Check
  const locales = ["en", "zh"];
  const hasLocale = locales.some(
    (locale) => pathname.startsWith(`/${locale}/`) || pathname === `/${locale}`
  );

  if (hasLocale) return;

  // 3. Default Locale Redirection
  // Redirect root / to /en, /playground to /en/playground, etc.
  request.nextUrl.pathname = `/en${pathname}`;
  return NextResponse.redirect(request.nextUrl);
}

export const config = {
  // Match all paths except internal Next.js paths
  // We handle specific file exclusions in the code logic above for better readability
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
