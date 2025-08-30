#!/usr/bin/env python3
"""
Single-shot solver for 'lucky_but_unlucky' (no brute force).
- Mirrors main()'s PRNG order: get 'lucky' first, then x inside run().
- Previews both values by snapshotting random state (no guessing).
- Uses FULLWIDTH digits so translate('0-9' -> '#') doesn't affect our inputs.
"""
import importlib.util, sys, builtins, os

TARGET_PATH = os.path.join(os.path.dirname(__file__), "lucky_but_unlucky", "lucky_but_unlucky.py")

def import_from_path(path, module_name="target_single"):
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod

def fw(n: int) -> str:
    return ''.join(chr(ord('０') + (ord(c) - ord('0'))) for c in str(n))

def main():
    mod = import_from_path(TARGET_PATH)
    rng = mod.random

    # 1) Mirror main(): lucky = random.getrandbits(32)
    state0 = rng.getstate()
    lucky32 = rng.getrandbits(32)

    # 2) The next call that run() makes is x = random.getrandbits(32)
    state_after_lucky = rng.getstate()
    x_preview = str(rng.getrandbits(32))

    # Restore to the exact states expected by run()
    rng.setstate(state_after_lucky)  # so run() will see the same x we previewed

    # Prepare scripted inputs: name = 'lucky' + x; numbers = FULLWIDTH zeros to keep d==e
    inputs = iter(['lucky' + x_preview, fw(0), fw(0)])
    _orig_input = builtins.input
    builtins.input = lambda prompt='': next(inputs)
    try:
        ans = mod.run(lucky32 % 10000)
    finally:
        builtins.input = _orig_input

    print(ans)

if __name__ == "__main__":
    main()
