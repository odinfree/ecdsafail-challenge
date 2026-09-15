#!/usr/bin/env python3
"""Decide whether the four-hole chart *readers* are faithful to the primitive.

Root audit lane's Q792-CHART-RAIL-CROSSCHECK.md asks for the one-script test:
take the primitive's own action (the 228-op PLAN in q792_mod16.rs), compute the
per-bit truth tables of its output groups over all 4096 chart codes, and compare
them with the shipped reader tables:

  * q793_exit_low::U16_TERMS          (u reader, bit 1..3 terms over 12 wires)
  * q793_exit_low::xor_r16's formula  (r reader, 16 inputs with A-case flags)

Verdict semantics:
  readers agree   -> the readers are exonerated; the mod8->mod16 traversal port
                     is the critical path (Q792-MOD16-PORT.md).
  readers differ  -> the readers are the defect and are cheap to fix.
"""
import re, sys, pathlib

SRC = pathlib.Path(__file__).resolve().parent / "repo" / "src" / "point_add" / "trailmix_port" / "inversion"
mod16 = (SRC / "q792_mod16.rs").read_text()
exit_low = (SRC / "q793_exit_low.rs").read_text()

plan_body = re.search(r"const PLAN: &\[\(usize, &\[i8\]\)\] = &\[(.*?)\n\];", mod16, re.S).group(1)
PLAN = [(int(t), [int(x) for x in re.findall(r"-?\d+", lits)])
        for t, lits in re.findall(r"\((\d+), &\[([-0-9,\s]*)\]\)", plan_body)]

def apply_plan(rails, echo_polarity=0):
    """rails: list of 14 bits (0..11 word, 12 guard, 13 echo). One PLAN pass."""
    r = list(rails)
    r[13] = echo_polarity
    for target, lits in PLAN:
        acc = 1
        for lit in lits:
            idx = abs(lit) - 1
            bit = r[idx] if idx < 13 else r[13]
            acc &= bit if lit > 0 else (1 - bit)
        tidx = 13 if target == 13 else target
        r[tidx] ^= acc
    return r

def mobius(table, nvars):
    t = table[:]
    for b in range(nvars):
        for m in range(len(t)):
            if m >> b & 1:
                t[m] ^= t[m ^ (1 << b)]
    return {m for m, on in enumerate(t) if on}

def bits_of(x, n):
    return [(x >> i) & 1 for i in range(n)]

def simulate():
    """Return (u_tables, r_tables) as 4-element lists of 4096-entry tables."""
    u = [[0] * 4096 for _ in range(4)]
    r = [[0] * 4096 for _ in range(4)]
    echo_dependent = False
    not_involutive = 0
    for code in range(4096):
        rails = bits_of(code, 12) + [1, 0]
        out = apply_plan(rails)
        for i in range(4):
            u[i][code] = out[i]
            r[i][code] = out[8 + i]
        out2 = apply_plan(out)
        if out2[:12] != rails[:12]:
            not_involutive += 1
        if apply_plan(rails, echo_polarity=1)[:12] != out[:12]:
            echo_dependent = True
    return u, r, echo_dependent, not_involutive

def scalar(code):
    t, b, v = code & 15, code >> 4 & 15, code >> 8 & 15
    if (t | v) & 1 == 0:
        return code
    m = 15
    inv = lambda a: next(x for x in range(1, 16, 2) if a * x % 16 == 1)
    if t & 1:
        u, r = b, (m - b * v) * inv(t) % 16
    else:
        u, r = (m - t * b) * inv(v) % 16, b
    return u | ((t if u & 1 else v) << 4) | (r << 8)

def scalar_tables():
    s = [scalar(c) for c in range(4096)]
    return [[(x >> i) & 1 for x in s] for i in range(4)], \
           [[(x >> (8 + i)) & 1 for x in s] for i in range(4)]

def parse_u16_terms():
    body = re.search(r"const U16_TERMS:&\[&\[u16\]\]=&\[(.*?)\n\];", exit_low, re.S).group(1)
    groups = re.findall(r"&\[([^\]]*)\]", body)
    return [{int(tok, 16) for tok in re.findall(r"0x[0-9a-fA-F]+", g)} for g in groups]

def xor_r16_formula(bit):
    """Mirror of q793_exit_low::xor_r16's per-bit function, flags cleared."""
    inv16 = [0, 1, 9, 11, 13, 13, 3, 7, 0, 9, 5, 3, 5, 5, 7, 15]
    inv16 = [0, 1, 9, 11, 13, 13, 3, 7, 0, 9, 5, 3, 5, 5, 7, 15]
    out = [0] * 4096
    for code in range(4096):
        t, b, v = code & 15, code >> 4 & 15, code >> 8 & 15
        r = (15 - b * v) * inv16[t] % 16 if t & 1 else b
        out[code] = r >> bit & 1
    return out

def main():
    u, r, echo_dep, not_inv = simulate()
    su, sr = scalar_tables()
    print(f"PLAN ops={len(PLAN)} echo_dependent={echo_dep} non_involutive_codes={not_inv}")
    print("primitive == documented scalar map:",
          all(u[i] == su[i] for i in range(4)) and all(r[i] == sr[i] for i in range(4)))
    u_terms = parse_u16_terms()
    print(f"U16_TERMS group sizes: {[len(g) for g in u_terms]}")
    ok = True
    for i in range(3):
        prim = mobius(u[1 + i], 12)
        same = prim == u_terms[i]
        ok &= same
        print(f"u bit{1+i}: primitive_terms={len(prim)} table_terms={len(u_terms[i])} "
              f"equal={same} missing_from_table={len(prim - u_terms[i])} extra={len(u_terms[i] - prim)}")
    r_ok = True
    for i in range(1, 4):
        prim = mobius(r[i], 12)
        reader = mobius(xor_r16_formula(i), 12)
        same = prim == reader
        r_ok &= same
        print(f"r bit{i}: primitive_terms={len(prim)} reader_terms={len(reader)} equal={same}")
    print()
    print("VERDICT:",
          "readers AGREE with the primitive (readers exonerated; traversal port is the critical path)"
          if (ok and r_ok) else
          "readers DIFFER from the primitive (readers are the defect)")
    return 0 if (ok and r_ok) else 1

if __name__ == "__main__":
    sys.exit(main())
