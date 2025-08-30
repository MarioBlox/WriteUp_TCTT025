#!/usr/bin/env python3
# one_shot_uploaded_solve.py (CLI path + auto-search, single-shot)
import os, sys, builtins, importlib.util, glob

def import_from_path(path, module_name="target_mod"):
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod

def to_fullwidth(n: int) -> str:
    return ''.join(chr(ord('０') + (ord(c) - ord('0'))) for c in str(n))

class NameValue:
    def __init__(self, get_x):
        self._get_x = get_x
    def __str__(self): return "lucky" + self._get_x()
    def replace(self, *_, **__): return "lucky" + self._get_x()
    def strip(self, *_, **__):   return "lucky" + self._get_x()
    def lower(self, *_, **__):   return "lucky" + self._get_x()
    def upper(self, *_, **__):   return "lucky" + self._get_x()
    def translate(self, *_, **__): return "lucky" + self._get_x()
    def isdigit(self): return False

def resolve_target():
    if len(sys.argv) > 1:
        p = os.path.abspath(sys.argv[1])
        if os.path.exists(p): return p
    base = os.path.dirname(os.path.abspath(__file__))
    cand = [
        os.path.join(base, "lucky_but_unlucky.py"),
        os.path.join(base, "lucky_but_unlucky", "lucky_but_unlucky.py"),
    ]
    for p in cand:
        if os.path.exists(p): return p
    hits = glob.glob(os.path.join(base, "**", "lucky_but_unlucky.py"), recursive=True)
    return os.path.abspath(hits[0]) if hits else None

def main():
    target_path = resolve_target()
    if not target_path or not os.path.exists(target_path):
        print("Target not found. Pass the path explicitly, e.g.:")
        print(r'  python one_shot_uploaded_solve.py ".\lucky_but_unlucky\lucky_but_unlucky.py"')
        sys.exit(1)

    mod = import_from_path(target_path)
    rng = mod.random

    last = {"x": ""}
    real_getrandbits = rng.getrandbits
    def hooked(bits):
        v = real_getrandbits(bits)
        last["x"] = str(v)
        return v
    rng.getrandbits = hooked

    B_int = 9007199254740991  # 2**53 - 1
    C_int = 9007199254740992  # 2**53
    B = to_fullwidth(B_int)
    C = to_fullwidth(C_int)

    orig_hash = builtins.hash
    def patched_hash(obj):
        if isinstance(obj, int): return 0
        return orig_hash(obj)
    builtins.hash = patched_hash

    calls = {"n": 0}
    orig_input = builtins.input
    def scripted_input(prompt=''):
        calls["n"] += 1
        if calls["n"] == 1: return NameValue(lambda: last["x"])
        return B if calls["n"] == 2 else C
    builtins.input = scripted_input

    try:
        lucky32 = rng.getrandbits(32)
        res = mod.run(lucky32 % 10000)
        print(res)
    finally:
        builtins.input = orig_input
        builtins.hash = orig_hash
        rng.getrandbits = real_getrandbits

if __name__ == "__main__":
    main()
