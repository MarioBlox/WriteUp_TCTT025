Lucky but Unlucky — FULL Package
================================
Included:
- one_shot_uploaded_solve.py   : Single-shot (CLI + auto-search). Handles buggy name check, float/hash traps.
- unlucky_one_shot_patched.py  : Single-shot. In-memory patch of name-check + FULLWIDTH numbers.
- one_shot_universal.py        : Single-shot. Hook + object to neutralize .replace() on name; FULLWIDTH numbers.
- one_shot_magic.py            : Single-shot. Magic string equals-everything; FULLWIDTH numbers.
- solve_lucky_single.py        : Single-shot using PRNG state mirroring (for proper upstream challenge).
- solve_lucky.py               : Reference brute-force variant (0..9999) for classic version.
- lucky_but_unlucky.zip        : Your original upload.
- lucky_but_unlucky/           : Extracted python from the zip (if present).
- lucky_but_unlucky.py         : The standalone file you uploaded (root).

Usage (recommended):
1) Try one_shot_uploaded_solve.py
   - auto-finds target or accept explicit path argument.
   - Example:
     python one_shot_uploaded_solve.py ".\lucky_but_unlucky\lucky_but_unlucky.py"

2) If the challenge is the pristine version from the event, use solve_lucky_single.py

Notes:
- FULLWIDTH digits (０–９) bypass ASCII-only translate() but still pass isdigit()/int().
- For float traps, 2**53-1 and 2**53 collapse to the same float value while remaining distinct ints.
- Hash trap neutralized by temporary monkeypatching builtins.hash for integers.
