#!/usr/bin/env python3
# solve_lucky.py (reference brute-force approach on lucky%10000)
import importlib.util, sys, builtins, os, re

TARGET_PATH = os.path.join(os.path.dirname(__file__), "lucky_but_unlucky", "lucky_but_unlucky.py")

def import_from_path(path, module_name="target_bf"):
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod

def fw(n: int) -> str:
    return ''.join(chr(ord('０') + (ord(c) - ord('0'))) for c in str(n))

def make_input_provider(responses):
    it = iter(responses)
    def _input(prompt=''):
        return next(it)
    return _input

def main():
    mod = import_from_path(TARGET_PATH)
    rng = mod.random
    # Snapshot and preview x
    state0 = rng.getstate()
    x = str(rng.getrandbits(32))
    rng.setstate(state0)

    b = fw(1234); c = fw(5678)
    for lucky in range(10000):
        rng.setstate(state0)
        inputs = ['lucky' + x, b, c]
        _orig_input = builtins.input
        builtins.input = make_input_provider(inputs)
        try:
            ans = mod.run(lucky)
        finally:
            builtins.input = _orig_input
        if isinstance(ans, str) and 'flag{' in ans:
            print(ans); return
    print("No flag found within 0..9999")

if __name__ == "__main__":
    main()
