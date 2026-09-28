#!/usr/bin/env python3
"""MSLU locale key-parity checker.

Executes data/locales.lua under Lua 5.1 with GetLocale() stubbed to each
client locale, dumps the effective MSLU.L table, and verifies every locale
block against the enUS base table:

  - zero missing keys (every locale carries exactly the enUS key set)
  - zero extra keys   (no locale invents keys enUS does not define)
  - zero values equal to the enUS value (nothing silently untranslated)

Also proves the structural fallback: an unsupported locale must yield a
table identical to enUS with no errors.

Usage: python3 tools/check_locale_parity.py [path/to/repo]
Exit code 0 = all checks passed; 1 = any failure.
"""

import os
import shutil
import subprocess
import sys
import tempfile

CLIENT_LOCALES = [
    "deDE", "esES", "esMX", "frFR", "itIT",
    "koKR", "ptBR", "ptPT", "ruRU", "zhCN", "zhTW",
]
FALLBACK_LOCALE = "xxXX"  # not a real WoW client locale

# Minimal Lua harness: stub GetLocale, load the addon locale file, dump the
# effective MSLU.L table as tab-separated key/value pairs (deterministic order).
HARNESS = r"""
function GetLocale() return "%s" end
MSLU = nil
dofile("%s")
local keys = {}
for k in pairs(MSLU.L) do keys[#keys + 1] = k end
table.sort(keys)
for _, k in ipairs(keys) do
    io.write(k, "\t", MSLU.L[k], "\n")
end
"""


def find_lua():
    for name in ("lua5.1", "lua"):
        path = shutil.which(name)
        if path:
            # "-" makes the interpreter read stdin as one chunk instead of
            # running interactive line-by-line mode (where local variables
            # do not survive between lines and the dump silently breaks).
            return [path, "-"]
    return None


def dump_table(lua_cmd, locales_lua, locale):
    """Run the harness for one locale; return {key: value}."""
    harness = HARNESS % (locale, locales_lua.replace("\\", "/"))
    proc = subprocess.run(
        lua_cmd, input=harness, capture_output=True, text=True, timeout=30
    )
    if proc.returncode != 0:
        raise RuntimeError(
            "lua failed for locale %s:\n%s\n%s" % (locale, proc.stdout, proc.stderr)
        )
    table = {}
    for line in proc.stdout.splitlines():
        key, _, value = line.partition("\t")
        table[key] = value
    if not table:
        raise RuntimeError("empty MSLU.L dump for locale %s" % locale)
    return table


def check(locale, base, actual):
    """Return list of problem strings for one locale against the enUS base."""
    problems = []
    missing = sorted(set(base) - set(actual))
    extra = sorted(set(actual) - set(base))
    same = sorted(k for k in base if k in actual and actual[k] == base[k])
    if missing:
        problems.append("missing keys: %s" % ", ".join(missing))
    if extra:
        problems.append("extra keys: %s" % ", ".join(extra))
    if same:
        problems.append("values equal to enUS: %s" % ", ".join(same))
    return problems


def main():
    repo = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), ".."
    )
    locales_lua = os.path.abspath(
        os.path.join(repo, "data", "locales.lua")
    )
    if not os.path.isfile(locales_lua):
        print("FATAL: data/locales.lua not found at %s" % locales_lua)
        return 1

    lua_cmd = find_lua()
    if not lua_cmd:
        print("FATAL: no lua5.1/lua interpreter on PATH")
        return 1

    failures = 0

    base = dump_table(lua_cmd, locales_lua, "enUS")
    print("enUS base table: %d keys" % len(base))
    for key in sorted(base):
        print("  %s" % key)

    for locale in CLIENT_LOCALES:
        actual = dump_table(lua_cmd, locales_lua, locale)
        problems = check(locale, base, actual)
        if problems:
            failures += 1
            print("%s: FAIL (%d/%d keys)" % (locale, len(actual), len(base)))
            for problem in problems:
                print("  - %s" % problem)
        else:
            print(
                "%s: OK (%d keys, 0 missing, 0 extra, 0 equal to enUS)"
                % (locale, len(actual))
            )

    fallback = dump_table(lua_cmd, locales_lua, FALLBACK_LOCALE)
    if fallback == base:
        print(
            "%s (unsupported locale): OK - effective table identical to enUS "
            "(%d keys)" % (FALLBACK_LOCALE, len(fallback))
        )
    else:
        failures += 1
        print(
            "%s (unsupported locale): FAIL - fallback table differs from enUS"
            % FALLBACK_LOCALE
        )

    print(
        "\nRESULT: %s (%d locale blocks checked, enUS base %d keys, "
        "fallback verified)" % (
            "PASS" if failures == 0 else "FAIL (%d locale(s))" % failures,
            len(CLIENT_LOCALES), len(base),
        )
    )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
