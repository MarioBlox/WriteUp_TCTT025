# 💿 Hidden Payload ISO — Rijndael + PowerShell XOR

โจทย์ซ่อนข้อมูลในอิมเมจ ISO9660/Joliet + Rock Ridge (ER) พร้อมใบ้กุญแจ **AES‑128** และ payload แบบ **PowerShell** 🧩  
เป้าหมาย: ไล่เก็บ hint → ถอด AES‑ECB → รันขั้นตอน XOR ตามสคริปต์ → ได้ **FLAG**

---

## 📁 ไฟล์โจทย์

| File | Size | SHA-256 |
|------|------|---------|
| `hidden_payload.iso` | 370688 bytes | `16429db3b0bdaa34b76dcf11072367d1133be0bd5407afa4fe4293aa46cb523c` |

---

## ⚡ TL;DR (ทำเร็ว เอาให้จบ)

1) อ่าน Rock Ridge *Extension Record* (ER) ใน ISO → จะเจอข้อความใบ้:   `Rijndael key (128-bit) = ASCII 'J' repeated and hex-encoded`  → คีย์ = `b"J"*16` (0x4A × 16)  
2) พบบล็อก **base64** (อยู่ในเซกเตอร์ต้น ๆ ของดิสก์) → ถอดเป็น **AES‑ECB ciphertext**  
3) ถอดรหัสด้วย **AES‑128/ECB** (คีย์ ‘J’×16) → ได้สคริปต์ **PowerShell** ที่ประกาศ   `$data = @(0x.., 0x.., ...)` และ `$key = 0x4A`  
4) ทำ **XOR** ไบต์ใน `$data` กับ `0x4A` → ได้ข้อความปลายทางที่มี **flag**

**✅ FLAG**
```
flag{powershell_xor_hidden_so_easy}
```

---

## 🧠 โครงเรื่อง (สั้นและชัด)

- โครงสร้าง ISO ใช้ Joliet/Rock Ridge; ข้อความใบ้ถูกซ่อนไว้ใน **Rock Ridge ER**  
- ciphertext ถูกซ่อนไว้เป็น **base64** ต่อเนื่อง (หนึ่ง–สองเซกเตอร์ติดกัน)  
- ถอด base64 → ได้บล็อกเข้ารหัส AES‑128 **ECB**; กุญแจคือ `'J'` × 16 ตามใบ้  
- plaintext คือ PowerShell ที่ใช้ `XOR` (`$key = 0x4A`) เพื่อปิดท้ายด้วยข้อความจริง

---

## 🐍 สคริปต์ตัวอย่าง (ค้น + ถอด + XOR)

```python
#!/usr/bin/env python3
import re, base64, pathlib
from Crypto.Cipher import AES

ISO = "hidden_payload.iso"
buf = pathlib.Path(ISO).read_bytes()

# 1) รวบ base64 ช่วงยาว ๆ ในอิมเมจ
b64_chunks = []
for m in re.finditer(rb"[A-Za-z0-9+/=](32,)", buf):
    s = m.group(0)
    try:
        base64.b64decode(s, validate=True)
        b64_chunks.append(s)
    except Exception:
        pass

# เลือกชิ้นที่ยาวที่สุดเป็น ciphertext
b64_chunks.sort(key=len, reverse=True)
cipher = base64.b64decode(b64_chunks[0])

# 2) ถอด AES-128 ECB (key = 'J' * 16)
key = b"J" * 16
plain = AES.new(key, AES.MODE_ECB).decrypt(cipher)

# 3) ดึงอาร์เรย์ PowerShell: $data = @(0x.., 0x.., ...); $key = 0x4A
m = re.search(rb"\$data\s*=\s*@\((0x[0-9A-Fa-f]2(?:\s*,\s*0x[0-9A-Fa-f]2)*)\).*?\$key\s*=\s*0x([0-9A-Fa-f]{2})", plain, re.S)
hex_list = m.group(1).decode()
xorkey = int(m.group(2), 16)

arr = [int(x,16) for x in re.findall(r"0x([0-9A-Fa-f]{2})", hex_list)]
out = bytes(b ^ xorkey for b in arr).decode("utf-8", errors="replace")
print(out)
```

> หมายเหตุ: ถ้า base64 กระจายหลายก้อน ให้ stitch ชิ้นที่อยู่ติดกัน/ในเซกเตอร์ใกล้ ๆ กันก่อนค่อยถอด

---

## 🛡️ Disclaimer

> ใช้เพื่อการศึกษา/แข่งขัน CTF เท่านั้น ห้ามใช้กับระบบจริงโดยไม่ได้รับอนุญาต

---

## ✨ Author

**marioblox** — *disk sneaky hunter* 🐾  
“อ่านเมทาดาทาให้ครบ ก่อนถอด crypto อย่างใจเย็น”
