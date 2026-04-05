"""
patch_melotts.py — Kaori Voice Studio MeloTTS compatibility patcher
====================================================================
MeloTTS imports all language modules (including Japanese) at startup.
Japanese requires MeCab and fugashi which cannot be compiled on Python 3.14
or on Windows without MeCab headers.

This patcher surgically fixes the three module-level lines in MeloTTS
that cause ImportError/AttributeError on systems without MeCab/fugashi.

Run automatically via:  kaori-melotts-patch  (console script)
Or manually:            python -m kaori_voice_studio.patch_melotts
"""

import site
import sys
from pathlib import Path


PATCHES = {
    # FILE: list of (old_string, new_string) pairs
    "melo/text/japanese.py": [
        # Patch 1 — MeCab import
        (
            "try:\n    import MeCab\nexcept ImportError as e:\n"
            "    raise ImportError(\"Japanese requires mecab-python3 and unidic-lite.\") from e",
            "try:\n    import MeCab\nexcept ImportError:\n    MeCab = None",
        ),
        # Patch 2 — MeCab.Tagger() instantiation
        (
            "_TAGGER = MeCab.Tagger()",
            "_TAGGER = MeCab.Tagger() if MeCab is not None else None",
        ),
        # Patch 3 — AutoTokenizer.from_pretrained at module level
        (
            "tokenizer = AutoTokenizer.from_pretrained(model_id)",
            "try:\n    tokenizer = AutoTokenizer.from_pretrained(model_id)\nexcept Exception:\n    tokenizer = None",
        ),
    ],
    "melo/text/cleaner.py": [
        # Patch 4 — import japanese alongside other languages
        (
            "from . import chinese, japanese, english, chinese_mix, korean, french, spanish",
            "try:\n    from . import chinese, japanese, english, chinese_mix, korean, french, spanish\n"
            "except ImportError:\n    from . import chinese, english, chinese_mix, korean, french, spanish\n"
            "    japanese = None",
        ),
    ],
}


def find_site_packages():
    """Return all site-packages directories to search."""
    dirs = []
    try:
        dirs += site.getsitepackages()
    except AttributeError:
        pass
    try:
        dirs.append(site.getusersitepackages())
    except AttributeError:
        pass
    return [Path(d) for d in dirs]


def apply_patches(verbose=True):
    """Apply all MeloTTS patches. Returns (patched, already_patched, not_found)."""
    site_dirs = find_site_packages()
    results = {"patched": [], "already_patched": [], "not_found": [], "melo_missing": False}

    # Check if melo is installed at all
    melo_found = any((d / "melo").exists() for d in site_dirs)
    if not melo_found:
        results["melo_missing"] = True
        if verbose:
            print("  MeloTTS not installed — skipping patches.")
        return results

    for rel_path, patches in PATCHES.items():
        # Find the file across all site-packages
        target = None
        for sd in site_dirs:
            candidate = sd / rel_path
            if candidate.exists():
                target = candidate
                break

        if target is None:
            results["not_found"].append(rel_path)
            if verbose:
                print(f"  Not found: {rel_path}")
            continue

        txt = target.read_text(encoding="utf-8")
        changed = False

        for old, new in patches:
            if old in txt:
                txt = txt.replace(old, new)
                changed = True
                if verbose:
                    print(f"  Patched:   {target.name} — {old[:40].strip()!r}...")
            # If old not found, either already patched or different version
            elif new not in txt:
                if verbose:
                    print(f"  Skipped:   {target.name} — pattern not found (different version?)")

        if changed:
            target.write_text(txt, encoding="utf-8")
            results["patched"].append(str(target))
        else:
            results["already_patched"].append(str(target))
            if verbose:
                print(f"  Already OK: {target.name}")

    return results


def main():
    print("\nKaori Voice Studio — MeloTTS compatibility patcher")
    print("─" * 50)

    results = apply_patches(verbose=True)

    if results["melo_missing"]:
        print("\nMeloTTS is not installed. Install it first:")
        print("  pip install git+https://github.com/myshell-ai/MeloTTS.git --no-deps")
        sys.exit(0)

    print()
    if results["patched"]:
        print(f"✓ Applied {len(results['patched'])} patch(es) successfully.")
    if results["already_patched"]:
        print(f"✓ {len(results['already_patched'])} file(s) already patched.")
    if results["not_found"]:
        print(f"⚠ {len(results['not_found'])} file(s) not found — may be a different MeloTTS version.")

    print("\nVerifying import...")
    try:
        from melo.api import TTS  # noqa: F401
        print("✓ MeloTTS imports successfully.")
    except Exception as e:
        print(f"✗ Import still failing: {e}")
        print("  You may need to apply additional patches manually.")
        sys.exit(1)

    print()


if __name__ == "__main__":
    main()
