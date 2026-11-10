/** Default example for Russian domestic phone input. */
export const PHONE_PLACEHOLDER = "8 912 345 67 89";

/** Digits only — for storage-agnostic comparisons. */
export function phoneDigits(phone: string | null | undefined): string {
  return (phone ?? "").replace(/\D/g, "");
}

/**
 * True when two phone strings refer to the same number.
 * Tolerates formatting and optional US country code (+1).
 */
export function phonesMatch(
  a: string | null | undefined,
  b: string | null | undefined,
): boolean {
  const da = phoneDigits(a);
  const db = phoneDigits(b);
  if (!da || !db) return false;
  if (da === db) return true;
  const national = (d: string) =>
    d.length === 11 && d.startsWith("1") ? d.slice(1) : d;
  const na = national(da);
  const nb = national(db);
  return na.length >= 10 && nb.length >= 10 && na.slice(-10) === nb.slice(-10);
}

/**
 * Default national input to `8 NXX XXX XX XX` while typing.
 * Preserve explicit international prefixes and existing eleven-digit US numbers.
 */
export function formatPhoneInput(raw: string): string {
  const digitsAll = raw.replace(/\D/g, "");
  if (!digitsAll) return "";

  if (raw.trimStart().startsWith("+") || (digitsAll.length === 11 && digitsAll.startsWith("1"))) {
    const country = digitsAll[0];
    if ((country !== "1" && country !== "7") || digitsAll.length > 11) return `+${digitsAll}`;
    const national = digitsAll.slice(1);
    const parts = country === "1"
      ? [national.slice(0, 3), national.slice(3, 6), national.slice(6, 10)]
      : [national.slice(0, 3), national.slice(3, 6), national.slice(6, 8), national.slice(8, 10)];
    return [`+${country}`, ...parts.filter(Boolean)].join(" ");
  }
  // Leave overlong input visible for validation rather than silently losing digits.
  if (digitsAll.length > 11) return digitsAll;
  const national = digitsAll.startsWith("8") ? digitsAll.slice(1) : digitsAll;
  const parts = [national.slice(0, 3), national.slice(3, 6), national.slice(6, 8), national.slice(8)].filter(Boolean);
  return ["8", ...parts].join(" ");
}
