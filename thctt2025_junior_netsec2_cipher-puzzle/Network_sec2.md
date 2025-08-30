# 🔐 Network_sec2 — Cipher Puzzle Chat

โจทย์เน็ตเวิร์กแนวน่ารัก: ข้อความแชตในพีแคปแอบแนบชิ้นส่วนเข้ารหัส (hex) มาให้เราต่อและถอดรหัส 🎯  
ปลายทางคือจดหมายทักทายและ **FLAG**

---

## 📁 ไฟล์โจทย์

| File | Size | SHA-256 |
|------|------|---------|
| `thctt2025_junior_netsec2_cipher-puzzle.pcapng` | 5480 bytes | `db1b1af4f059fce0144c114190ddacafa195fe976d12373a54c132759eb9085a` |

---

## ⚡ TL;DR (ทำเร็ว เอาให้จบ)

1) ค้นสตริงใน PCAP จะเจอหลายบรรทัดรูปแบบ `CIPHER_PART;part=N;data=<HEX>`  
2) เรียงตาม `part` แล้วแปลง `HEX → bytes` ต่อกันให้ได้ `ciphertext`  
3) ถอดแบบ **repeating‑key XOR** ด้วยคีย์ `mango` → จะได้ plaintext เต็ม  
4) อ่านบรรทัดที่มี **flag**

**✅ FLAG**
```
flag{50fba860c6c53436cbaffe8391619e67}
```

---

## 🧠 ไอเดีย/กับดัก (สรุปสั้นและตรงประเด็น)

- บทสนทนาในพีแคป (บรรทัดที่ขึ้นต้นด้วย `CHAT;msg=...`) เป็น **ตัวหลอก**  
- ของจริงคือบรรทัด `CIPHER_PART;part=N;data=...` ซึ่งเป็น **ชิ้นส่วนข้อมูลฐาน 16**  
- เมื่อประกอบครบ จะได้บล็อบที่ไม่ได้อ่านตรง ๆ (มีไบต์ต่ำกว่า 0x20 เยอะ) ⇒ ส่อว่าเป็น **XOR cipher**  
- จัดการด้วย **known‑plaintext attack** สมมุติว่ามีคำว่า `flag{` อยู่ในข้อความ → ไล่หาคีย์ซ้ำ → พบว่าเป็น `mango`

---

## 🪜 Step-by-step (เข้าใจง่าย)

### 1) ดึงชิ้นส่วนจาก PCAP
ใช้ `strings` หรือเปิดใน Wireshark แล้วค้นคำว่า `CIPHER_PART` จะเห็นเช่น:
```
CIPHER_PART;part=1;data=2504020b004d071c0e0a0305426d65210e00002c
...
CIPHER_PART;part=6;data=55525756595c580b5158106b
```

### 2) รวมเป็น ciphertext
- เรียงตามหมายเลข `part=1..6`
- ตัดส่วนหลัง `data=` ของแต่ละอัน ต่อกัน แล้ว `hex → bytes`

### 3) ถอดด้วย repeating‑key XOR
- ใช้คีย์ `mango` (ตัวเล็กทั้งหมด)
- ได้ข้อความทักทายและบรรทัด **FLAG**

ตัวอย่าง plaintext (บางส่วน):
```
Hello friend,

LongCat is here.
I have ... message for you. 

flag{50fba860c6c53436cbaffe8391619e67}
```

---

## 🐍 สคริปต์ Python (พร้อมใช้)

```python
#!/usr/bin/env python3
import re, binascii

pcap = "thctt2025_junior_netsec2_cipher-puzzle.pcapng"
buf = open(pcap, "rb").read()

parts = sorted(
    (int(m.group(1)), bytes.fromhex(m.group(2).decode()))
    for m in re.finditer(rb"CIPHER_PART;part=(\d+);data=([0-9A-Fa-f]+)", buf)
)

cipher = b"".join(b for _, b in parts)
key = b"mango"
plain = bytes(c ^ key[i % len(key)] for i, c in enumerate(cipher))
print(plain.decode(errors="replace"))
```

> ถ้าต้องการพิสูจน์คีย์แบบไม่ต้องเดา ใช้ **known‑plaintext**: ลองแทนที่บางตำแหน่งด้วย `flag{` เพื่อถอดคีย์ซ้ำ แล้วทดสอบกับทั้งบล็อบ

---

## 🛡️ Disclaimer

> ใช้เพื่อการศึกษา/แข่งขัน CTF เท่านั้น ห้ามใช้กับระบบจริงโดยไม่ได้รับอนุญาต

---

## ✨ Author

**marioblox** — *cipher tamer* 🐱‍👤  
“ต่อชิ้นส่วนให้ครบ แล้วค่อยถอดด้วยใจเย็น ๆ”
