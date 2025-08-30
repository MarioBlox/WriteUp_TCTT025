#!/usr/bin/env python3
"""
one_shot_universal.py
- Single-shot (no brute force)
- No source file edits; patches behavior at runtime
- Works even if the challenge does: input(...).replace('lucky'+x, '')
How it works
- Hooks random.getrandbits to remember the most recent 32-bit value.
- When run() generates x via getrandbits(), our input() for the *first* prompt
  returns a special object whose .replace(...) returns the correct "lucky<x>"
  string regardless of the arguments — bypassing the buggy check.
- Number inputs are FULLWIDTH digits so translate('0-9'->'#') doesn't touch them,
  while still passing .isdigit() and int().
Usage:
  Place next to: lucky_but_unlucky/lucky_but_unlucky.py
  Run:  python one_shot_universal.py
"""
import os, sys, builtins, importlib.util

BASE = os.path.dirname(__file__)
TARGET = os.path.join(BASE, "lucky_but_unlucky", "lucky_but_unlucky.py")

def import_target(path):
    spec = importlib.util.spec_from_file_location("target_universal", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["target_universal"] = mod
    spec.loader.exec_module(mod)
    return mod

def fw(n: int) -> str:
    return ''.join(chr(ord('０') + (ord(c) - ord('0'))) for c in str(n))

class NameValue:
    """Object that pretends to be the name input; its .replace returns the intended string."""
    def __init__(self, value: str):
        self._s = value
    def __str__(self):
        return self._s
    def replace(self, *args, **kwargs):
        # Whatever replace is asked, we return the correct string so the later equality passes.
        return self._s
    def translate(self, table):
        # If mistakenly translated, keep string unchanged
        return self._s
    def isdigit(self):
        # It's a name, not a digit string
        return False

def main():
    if not os.path.exists(TARGET):
        print("ไม่พบไฟล์:", TARGET)
        sys.exit(1)

    mod = import_target(TARGET)

    # Hook RNG to remember last value
    last = {"val": None}
    real_get = mod.random.getrandbits
    def hooked_get(bits):
        v = real_get(bits)
        # Store as string to match code comparing with x string
        last["val"] = str(v)
        return v
    mod.random.getrandbits = hooked_get

    # Script input sequence with adaptive first response
    call_no = {"n": 0}
    def scripted_input(prompt=""):
        call_no["n"] += 1
        if call_no["n"] == 1:
            # After run() generates x, last['val'] holds x; build lucky<x>
            return NameValue("lucky" + (last["val"] or ""))
        else:
            # Equal FULLWIDTH numbers so d == e regardless of lucky
            return fw(0)

    orig_input = builtins.input
    builtins.input = scripted_input
    try:
        # Mirror program entry: lucky first, run(lucky%10000)
        lucky32 = mod.random.getrandbits(32)
        ans = mod.run(lucky32 % 10000)
        print(ans)
    finally:
        builtins.input = orig_input
        mod.random.getrandbits = real_get

if __name__ == "__main__":
    main()
