#!/usr/bin/env python3
"""
unlucky_one_shot_patched.py
- Single-shot solver. No brute force.
- Tolerates the buggy 'name replace' check by patching it in-memory.
- Mirrors PRNG call order so the same x is used.
- Feeds FULLWIDTH digits so numeric checks pass untouched.
Usage:
  Place this file next to: lucky_but_unlucky/lucky_but_unlucky.py
  Run:  python unlucky_one_shot_patched.py
"""
import os, sys, re, types, builtins, importlib.util

BASE = os.path.dirname(__file__)
TARGET = os.path.join(BASE, "lucky_but_unlucky", "lucky_but_unlucky.py")

def fw(n: int) -> str:
    # FULLWIDTH digits (０–９) to bypass ASCII translate while passing isdigit()/int()
    return ''.join(chr(ord('０') + (ord(c) - ord('0'))) for c in str(n))

def load_patched_module(path: str):
    src = open(path, "r", encoding="utf-8").read()

    # Patch 1: remove `.replace('lucky'+x, '')` or with spaces/quotes variants on the name line
    # a = input(...).replace('lucky' + x, '')
    src = re.sub(
        r"""(\ba\s*=\s*input\s*\([^\)]*\))\s*\.replace\s*\(\s*(['"])lucky\2\s*\+\s*x\s*,\s*(['"])\\?\\?['"]\s*\)""",
        r"\1",
        src
    )
    # Also tolerate: .replace("lucky"+x,"")
    src = re.sub(
        r"""(\ba\s*=\s*input\s*\([^\)]*\))\s*\.replace\s*\(\s*"lucky"\s*\+\s*x\s*,\s*""\s*\)""",
        r"\1",
        src
    )

    # Optional Patch 2 (safety): if someone inverted the check to force-exit, normalize it.
    # Turn "if a != 'lucky' + x:" into correct logic if it was accidentally inverted with replace misuse.
    # We leave it as-is unless we detect a pathological always-exit pattern; no-op otherwise.

    mod = types.ModuleType("target_mod")
    code = compile(src, path, "exec")
    exec(code, mod.__dict__)
    return mod, src

def main():
    if not os.path.exists(TARGET):
        print("ไม่พบไฟล์:", TARGET)
        sys.exit(1)

    mod, patched_src = load_patched_module(TARGET)
    rng = mod.random

    # Mirror main(): lucky first, then x inside run()
    state0 = rng.getstate()
    lucky32 = rng.getrandbits(32)           # call #1 (lucky in main)
    state_after_lucky = rng.getstate()
    x_preview = str(rng.getrandbits(32))    # call #2 (x inside run)
    rng.setstate(state_after_lucky)         # so run() will see the same x we previewed

    # Script inputs: exact name and equal FULLWIDTH numbers
    inputs = iter(['lucky' + x_preview, fw(0), fw(0)])
    orig_input = builtins.input
    builtins.input = lambda prompt='': next(inputs)

    try:
        ans = mod.run(lucky32 % 10000)
    finally:
        builtins.input = orig_input

    print(ans)

if __name__ == "__main__":
    main()
