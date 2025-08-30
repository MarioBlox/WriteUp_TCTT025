Lucky but Unlucky — CTF Package
--------------------------------
Files:
- solve_lucky_single.py : Single-shot solver (no brute-force). Mirrors PRNG order,
  previews lucky & x via random.getstate()/setstate(), and feeds FULLWIDTH digits.
- solve_lucky.py        : Brute-force on lucky%10000 (for reference).
- lucky_but_unlucky.zip : The original archive as uploaded.
- lucky_but_unlucky/lucky_but_unlucky.py : Extracted source from the archive.

Usage (single-shot):
1) Place lucky_but_unlucky/lucky_but_unlucky.py (full, untampered) next to solve_lucky_single.py
2) Run:  python3 solve_lucky_single.py
3) The script will print the program's response (should include flag).

Notes:
- Uses FULLWIDTH digits (０–９) to pass .translate('0-9'->'#') while still satisfying .isdigit()/int().
- If your target file had ellipses '...' (truncated), replace it with the full version from the challenge.
