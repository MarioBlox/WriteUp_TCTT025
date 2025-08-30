# 🧩 Network_sec1 — Love Letter in the Packets

โจทย์เน็ตเวิร์ก (น่ารักแต่ไม่อ่อนโยน) ที่ซ่อน “จดหมายรัก” ไว้ในทราฟฟิก `pcapng` เป้าหมายคือดึงไฟล์ที่ถูกแยกชิ้นส่วนในแพ็กเก็ตออกมาให้ครบ แล้วอ่าน Flag

---

## 📁 ไฟล์โจทย์

| File | Size | SHA-256 |
|------|------|---------|
| `thctt2025_junior_netsec1_love-letter1.pcapng` | 8,823 bytes | `5952c5ef66faaa9b0ab519af23d11af186c23ce2ba473cb7f2203b66ea8fe07e` |

---

## ⚡ TL;DR (ทำเร็ว เอาให้จบ)

```bash
# 1) ดึงและเรียงชิ้นส่วน Base64 (ตามหมายเลข part)
strings -n 8 thctt2025_junior_netsec1_love-letter1.pcapng | grep 'BLOCK_UPDATE;id=chair;part=' | sort -t= -k2,2n | sed 's/.*data=//g' | tr -d '\n' > payload.b64

# 2) ถอด Base64 → ได้ ZIP
base64 -d payload.b64 > payload.zip

# 3) เปิดไฟล์จดหมายใน ZIP
unzip -p payload.zip love_letter.txt
```

**✅ Flag**
```
flag{f0b3e7e3568616fa6d4a22ad0ed4c89e}
```

---

## 🧠 ไอเดียหลัก (สั้นและตรงประเด็น)

- ในแพ็กเก็ตมีสตริงลักษณะนี้กระจายอยู่หลายอัน:
  ```
  BLOCK_UPDATE;id=chair;part=<N>;data=<BASE64>
  ```
- ฟิลด์ `data=` คือ **Base64** ที่ถูก “หั่น” เป็นหลายชิ้น (part=1..11)  
- เมื่อต่อเรียงถูกลำดับแล้วถอด Base64 จะได้ไฟล์ **ZIP** ซึ่งมี `love_letter.txt` ซ่อน Flag อยู่

> สังเกตต้นสตริง Base64 มักขึ้นต้น `UEs...` (คือ “PK” ของ ZIP)

---

## 🪜 Step-by-step (เข้าใจง่าย)

### 1) ค้นเบาะแสใน pcap
- เปิดใน **Wireshark** → `Ctrl+F` → เลือก **String** + **Packet bytes**  
- ค้นคำว่า `BLOCK_UPDATE` จะเห็นหลายแพ็กเก็ตหน้าตาแบบนี้:
  ```
  BLOCK_UPDATE;id=chair;part=1;data=UEsDBBQAAAAI...
  BLOCK_UPDATE;id=chair;part=2;data=RZFBb9s...
  ...
  BLOCK_UPDATE;id=chair;part=11;data=bG92ZV9sZXR0ZXIudHh0UEsFBg...
  ```

### 2) รวม Base64 ตามลำดับ part
- ดึงเฉพาะค่าหลัง `data=` ของทุกแพ็กเก็ต
- **เรียง** ตาม `part=1 → part=N`
- นำมาต่อกันเป็นบรรทัดเดียว → `payload.b64`

### 3) ถอดรหัสและอ่านไฟล์
```bash
base64 -d payload.b64 > payload.zip
unzip -l payload.zip
unzip -p payload.zip love_letter.txt
```
จะพบข้อความจดหมาย พร้อม **Flag** ตอนท้าย

---

## 🧰 เครื่องมือที่ใช้ได้

- **Wireshark** — ค้นแพ็กเก็ต/สตริง
- **CLI** — `strings`, `grep`, `sort`, `sed`, `base64`, `unzip`
- **CyberChef** — “From Base64” → “Extract Files” (ลาก Base64 ที่ต่อกันแล้วเข้าไป)

---

## 🐍 สคริปต์ Python (ตัวเลือกเสริม)

```python
import re, base64, io, zipfile

pcap = "thctt2025_junior_netsec1_love-letter1.pcapng"
raw = open(pcap, "rb").read()

parts = sorted(
    (int(m.group(1)), m.group(2).decode())
    for m in re.finditer(rb"BLOCK_UPDATE;id=chair;part=(\d+);data=([A-Za-z0-9+/=]+)", raw)
)

b64 = "".join(b for _, b in parts)
zip_bytes = base64.b64decode(b64)
with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
    print(z.read("love_letter.txt").decode())
```

---

## 📝 บทเรียนสั้นๆ

- เห็น Base64 ขึ้นต้น `UEs` ให้คิดถึง ZIP (`PK`)
- โจทย์ Forensics ชอบ “ซอยข้อมูลเป็นชิ้นๆ” ในแพ็กเก็ต → ต้อง **เรียงลำดับ** ให้ถูกก่อนถอด
- CLI สามารถแก้โจทย์ได้ครบในไม่กี่คำสั่ง (เร็วและตรวจซ้ำง่าย)

---

## 🛡️ Disclaimer

> เนื้อหานี้เพื่อการศึกษา/แข่งขัน CTF เท่านั้น ห้ามนำเทคนิคไปใช้กับระบบจริงโดยไม่ได้รับอนุญาต

---

## ✨ Author

**marioblox** — *packet whisperer*  
“จับสัญญาณให้ได้เรื่อง แล้วเรื่องจะเล่า Flag ให้เราเอง”
