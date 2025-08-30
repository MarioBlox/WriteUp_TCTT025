# 💌 Network_sec3 — Love Letter 2 (STH Protocol v1)

โจทย์เน็ตเวิร์กภาคต่อ: เซิร์ฟเวอร์ส่ง “จดหมายรัก” ผ่านโปรโตคอล **STH v1** บน UDP ให้เราต่อชิ้นส่วน ถอดรหัส และคลายบีบอัดจนได้ข้อความจริง 🧩✨

---

## 📁 ไฟล์โจทย์

| File | Size | SHA-256 |
|------|------|---------|
| `thctt2025_junior_netsec3_love-letter-2.pcapng` | 2232 bytes | `8fba934db05b7a4f85609fb3e7c07958483f8c09c96bac552be34eb7b60d0e26` |
| `thctt2025_junior_netsec3_love-letter-2_protocol-spec-v1.txt` | 6038 bytes | `2a9344d0cd8e853d7eb68f677abe6212df2783f45865520877b6081c2a6b65c8` |

---

## ⚡ TL;DR (ทำเร็ว เอาให้จบ)

```bash
python3 solve_sth_netsec3.py thctt2025_junior_netsec3_love-letter-2.pcapng
```

สคริปต์จะ: ดึง UDP payload → ตรวจ STH header+CRC32 → เลือก session ที่ครบ → เรียงชิ้นด้วย LCG → สร้าง keystream (SHA‑256 counter) → XOR → `zlib.decompress` → ได้ plaintext

**✅ FLAG**
```
flag{ba003b057dc0fabbf4511fef456968f0}
```

---

## 🧠 โครงสร้างโปรโตคอล (สรุปสั้นและตรงประเด็น)

- **Transport**: UDP; เซิร์ฟเวอร์ฟังที่ **31337** และตอบกลับไปยังพอร์ตชั่วคราวของไคลเอนต์  
- **Endianness**: ค่าหลายไบต์เป็น **big‑endian**  
- **Header (19 bytes)**: `magic="STH"(3) | ver(1) | type(1) | session_id(4) | seq(4) | payload_len(2) | crc32(4)`  
  `crc32` ตรวจบน `header[:15] + payload` (อยู่ในเฮดเดอร์ ไม่ใช่ท้ายแพ็กเก็ต)
- **HELLO/WELCOME**: WELCOME ให้ `server_nonce(8)`, `salt(8)`, `chunk_size(2)`, `total_chunks(2)`, `a,c,seed (4 each)`, และ `hint`
- **Permutation (LCG)**: `x0=seed % n; x_(k+1)=(a*x_k + c) mod n` ต้องเป็น permutation เต็ม 0..n-1  
  ใช้ `order[j]=i` เพื่อแมป DATA `seq=j` กลับไปตำแหน่งดัชนีเดิม `i`
- **Cipher & Compression**:  
  1) บีบอัดด้วย **zlib** → `plaintext_cmp`  
  2) Keystream: `SHA256(session_id || client_nonce || server_nonce || salt || k_be32)` ต่อบล็อกจนยาวพอ  
  3) ถอดด้วย `ciphertext XOR keystream` → ได้ `plaintext_cmp` → `zlib.decompress` เป็น **plaintext**

---

## 🐍 `solve_sth_netsec3.py` (พร้อมใช้งาน)

> ฟังก์ชันหลัก: ดึง payload ด้วย `tshark` → parse STH/CRC32 → สร้างลำดับ LCG → ประกอบ ciphertext → สร้าง keystream → XOR → zlib.decompress → พิมพ์ plaintext

```python
#!/usr/bin/env python3
import sys, subprocess, binascii, struct, zlib, hashlib

MAGIC = b"STH"
VER = 1

def run_tshark(path):
    cmd = ["tshark", "-nr", path, "-Y", "udp && data",
           "-T", "fields", "-e", "udp.srcport", "-e", "udp.dstport", "-e", "data", "-E", "separator=,"]
    out = subprocess.check_output(cmd, text=True)
    recs = []
    for line in out.strip().splitlines():
        parts = line.split(",")
        if len(parts) < 3 or not parts[2]:
            continue
        try:
            src = int(parts[0]); dst = int(parts[1])
        except:
            src = dst = 0
        data = binascii.unhexlify(parts[2])
        recs.append((src, dst, data))
    return recs

def crc32_ieee(b): return zlib.crc32(b) & 0xFFFFFFFF

def parse_header(pkt):
    if len(pkt) < 19: return None
    magic, ver, typ = pkt[:3], pkt[3], pkt[4]
    if magic != MAGIC or ver != VER: return None
    session_id, seq, payload_len, crc = struct.unpack(">I I H I", pkt[5:19])
    payload = pkt[19:19+payload_len]
    if len(payload) != payload_len: return None
    if crc32_ieee(pkt[:15] + payload) != crc: return None
    return dict(type=typ, sid=session_id, seq=seq, payload=payload)

def lcg_order(a, c, seed, n):
    seen, order = set(), []
    x = seed % n
    for _ in range(n):
        if x in seen: return None
        seen.add(x); order.append(x)
        x = (a * x + c) % n
    return order if len(order) == n else None

def derive_keystream(sid_be4, cnonce8, snonce8, salt8, length):
    out, k = bytearray(), 0
    while len(out) < length:
        blk = hashlib.sha256(sid_be4 + cnonce8 + snonce8 + salt8 + struct.pack(">I", k)).digest()
        out.extend(blk); k += 1
    return bytes(out[:length])

def main():
    if len(sys.argv) < 2:
        print("Usage: solve_sth_netsec3.py file.pcapng", file=sys.stderr); sys.exit(1)
    records = run_tshark(sys.argv[1])

    last_client_nonce, sessions = None, {}

    for src, dst, raw in records:
        h = parse_header(raw)
        if not h: continue
        typ, sid, seq, payload = h["type"], h["sid"], h["seq"], h["payload"]

        if typ == 0x01:  # HELLO
            if len(payload) >= 8:
                last_client_nonce = payload[:8]
        elif typ == 0x02:  # WELCOME
            if len(payload) != 34: continue
            server_nonce = payload[0:8]; salt = payload[8:16]
            chunk_size, total_chunks, a, c, seed, hint = struct.unpack(">HHIIIH", payload[16:34])
            if hint != 0xB1B2: continue
            sessions[sid] = dict(client_nonce=last_client_nonce, server_nonce=server_nonce, salt=salt,
                                 chunk_size=chunk_size, total_chunks=total_chunks, a=a, c=c, seed=seed,
                                 data_by_seq={})
        elif typ == 0x10:  # DATA
            if sid in sessions:
                sessions[sid]["data_by_seq"][seq] = payload
        elif typ == 0x20:  # BYE
            pass

    chosen = None
    for sid, S in sessions.items():
        if S["client_nonce"] is None: continue
        if len(S["data_by_seq"]) == S["total_chunks"]:
            chosen = (sid, S); break
    if not chosen:
        print("No complete session found.", file=sys.stderr); sys.exit(2)

    sid, S = chosen; n = S["total_chunks"]
    order = lcg_order(S["a"], S["c"], S["seed"], n)
    if not order: print("Invalid LCG order.", file=sys.stderr); sys.exit(3)

    parts = [b""] * n
    for j, chunk in S["data_by_seq"].items():
        if 0 <= j < n:
            i = order[j]; parts[i] = chunk
    ciphertext = b"".join(parts)

    ks = derive_keystream(struct.pack(">I", sid), S["client_nonce"], S["server_nonce"], S["salt"], len(ciphertext))
    cmp_plain = bytes(c ^ k for c, k in zip(ciphertext, ks))

    try:
        plain = zlib.decompress(cmp_plain)
    except Exception as e:
        print("Decompress failed:", e, file=sys.stderr); sys.exit(4)

    sys.stdout.buffer.write(plain)

if __name__ == "__main__":
    main()
```

---

## 📝 เคล็ดลับ/กับดัก

- ยืนยัน **CRC32** ทุกแพ็กเก็ตก่อนใช้งาน (อยู่ท้ายส่วนเฮดเดอร์)  
- เลือก **session** ที่ `total_chunks` ครบ และ `hint` ถูกต้อง  
- ตรวจว่า LCG ให้ **permutation เต็ม** 0..n‑1 ก่อนประกอบข้อมูล

---

## 🛡️ Disclaimer

> ใช้เพื่อการศึกษา/แข่งขัน CTF เท่านั้น ห้ามใช้กับระบบจริงโดยไม่ได้รับอนุญาต

---

## ✨ Author

**marioblox** — *packet romantic* 💘  
“ต่อชิ้นส่วนอย่างใจเย็น แล้วความรัก (flag) จะเผยตัวเอง”
