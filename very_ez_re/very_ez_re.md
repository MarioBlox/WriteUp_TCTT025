# 🧸 very_ez_re — Very Easy RE (NET8)

โจทย์รีเวิร์ส .NET 8 โครงสร้างเรียบง่าย เน้นอ่านโค้ดและคิดตรงประเด็น 🎯  
เป้าหมาย: วิเคราะห์แอสเซมบลีและดึง **Flag** ออกมาอย่างถูกต้อง (ไม่เดา)

---

## 📁 ไฟล์โจทย์

| File | Purpose |
|------|---------|
| `very_ez_re.exe` | ไบนารีหลัก (Windows PE, .NET 8) |
| `very_ez_re.dll` | แอสเซมบลีหลัก ใช้ decompile/patch ได้สะดวก |
| `very_ez_re.pdb` | สัญลักษณ์ดีบัก (ช่วยเห็นชื่อไฟล์/เมธอด เช่น `Program.cs`) |
| `very_ez_re.runtimeconfig.json` | ระบุ Target Framework/Runtime (net8.0) |
| `very_ez_re.deps.json` | รายละเอียด dependency ของแอป |

> จากการ decompile พบ namespace `CTFChallenge` และคลาส `Program` พร้อมเมธอดสำคัญหลายตัว

---

## ⚡ TL;DR (ทางลัดเร็วและชัวร์)

**ตัวจริงอยู่ที่ Base64 ในตัวแปร `encodedSecret`** — ถอดแล้วคือ Flag ทันที:

```csharp
private static readonly string encodedSecret = "ZmxhZ3szNTE2NzJhNDQ5YzhmMjdlYWMxZTUzNTJhZmI4ZWNjMX0=";
```

ถอด Base64 → UTF‑8:
```text
flag{351672a449c8f27eac1e5352afb8ecc1}
```

**✅ Flag**
```
flag{351672a449c8f27eac1e5352afb8ecc1}
```

> หมายเหตุ: มีเมธอด/สตริงหลอก (`GenerateDecoy()` → `"ZmFrZV9mbGFne3RoaXNfaXNfbm90X3JlYWx9"` ซึ่งถอดได้เป็น `fake_flag{this_is_not_real}`) อย่าหลงเชื่อ

---

## 🧠 โครงสร้างลอจิก (สรุปสั้นและตรงประเด็น)

เมธอดสำคัญที่พบใน `Program`:
- `ValidatePassword(string input)` → เช็กอินพุตกับ `passwordEnter` (array 12 ไบต์)  
  สร้างผ่าน static ctor ด้วย `RuntimeHelpers.InitializeArray(...)` → ทำให้เดายากเล็กน้อยถ้าไม่อ่าน IL
- `RevealFlag()` → ถอด `encodedSecret` (Base64) แล้ว `Console.WriteLine()` ตัวจริง
- `GenerateDecoy()` → คืน Base64 ที่เป็น **ธงปลอม**
- `CheckDecoyPassword(string input)` → คืนค่า `true` หาก `password123`/`admin`/`flag` แต่ **ไม่ได้ถูกเรียกใช้จริงในการแสดงธงจริง**

> สรุป: แม้จะป้อนรหัสผ่าน “หลอก” ให้ผ่านเงื่อนไข decoy ได้ แต่ถ้าไม่ผ่าน `ValidatePassword` ก็จะไม่เรียก `RevealFlag()` อยู่ดี ดังนั้น **อ่าน/ถอด `encodedSecret` ตรง ๆ** คือวิธีที่เร็วและถูกต้องที่สุด

---

## 🪜 ขั้นตอนทำแบบย่อ (2 ทางเลือก)

### วิธีที่ 1 — ถอด Base64 ตรง ๆ (แนะนำ)
1) เปิด DLL ด้วย ILSpy/dnSpy → ไปที่ `Program`  
2) อ่านค่าคงที่ `encodedSecret`  
3) ถอด Base64 → ได้ Flag

ตัวอย่างด้วย Python:
```python
import base64
s = "ZmxhZ3szNTE2NzJhNDQ5YzhmMjdlYWMxZTUzNTJhZmI4ZWNjMX0="
print(base64.b64decode(s).decode())
# -> flag{351672a449c8f27eac1e5352afb8ecc1}
```

### วิธีที่ 2 — Patch ให้โปรแกรมโชว์เอง
1) เปิด `very_ez_re.dll` ใน **dnSpy**  
2) แก้ `ValidatePassword(string s)` ให้ `return true;` เสมอ  
3) Build module แล้วรัน `very_ez_re.exe` → โปรแกรมจะเรียก `RevealFlag()` และพิมพ์ Flag

---

## 🧰 เครื่องมือที่ใช้ได้
- **dnSpy** — decompile/patch/รีบิลด์
- **ILSpy / ilspycmd** — decompile เร็วและเบา
- **Ghidra (w/ DotNet)** — วิเคราะห์ IL/สตริง/เมทาดาทา
- **strings/grep** — ไล่หาเบาะแส (`encodedSecret`, `RevealFlag`, ฯลฯ)

---

## 🛡️ Disclaimer
> ใช้เพื่อการศึกษา/แข่งขัน CTF เท่านั้น ห้ามใช้กับระบบจริงโดยไม่ได้รับอนุญาต

---

## ✨ Author
**marioblox** — *RE with a smile* 😺  
“อ่านตรงจุด แพตช์เท่าที่จำเป็น และเช็คธงอย่างมีหลักฐาน”
