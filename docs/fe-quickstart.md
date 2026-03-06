# คู่มือเชื่อมต่อ API สำหรับทีม FE

---

## 1. Base URL

| Environment         | URL                         | หมายเหตุ             |
| ------------------- | --------------------------- | -------------------- |
| **Staging** (ทดสอบ) | `http://localhost:2531/api` | ใช้ตัวนี้ระหว่าง dev |
| **Production**      | `http://localhost:2530/api` | deploy จริงเท่านั้น  |

> **Android Emulator** → เปลี่ยน `localhost` เป็น `10.0.2.2`  
> **iOS Simulator** → ใช้ `127.0.0.1` ได้ปกติ

---

## 2. Test Account (Staging)

```
email:    admin@ytrc.co.th
password: Admin@1234
```

---

## 3. Auth Flow

### 3.1 Login

```
POST /auth/login
```

**Request**

```json
{
  "email": "admin@ytrc.co.th",
  "password": "Admin@1234"
}
```

**Response (200)**

```json
{
  "accessToken": "eyJ...",
  "refreshToken": "eyJ...",
  "user": {
    "id": "uuid",
    "email": "admin@ytrc.co.th",
    "username": "admin",
    "firstName": "Admin",
    "lastName": "YTRC",
    "displayName": null,
    "role": "staff_1",
    "permissions": [],
    "department": null,
    "status": "ACTIVE"
  }
}
```

**ข้อผิดพลาดที่ต้อง handle:**

| HTTP | detail                                        | ความหมาย             | วิธีรับมือ                         |
| ---- | --------------------------------------------- | -------------------- | ---------------------------------- |
| 401  | `"User not found"`                            | ไม่พบ email นี้      | แจ้ง "อีเมลหรือรหัสผ่านไม่ถูกต้อง" |
| 401  | `"Password incorrect. N attempts remaining."` | รหัสผิด              | แจ้งจำนวนครั้งที่เหลือ             |
| 401  | `"Account has been locked..."`                | login ผิด 5 ครั้ง    | แจ้งให้ติดต่อ admin                |
| 401  | `"Account is locked..."`                      | สถานะ SUSPENDED      | แจ้งให้ติดต่อ admin                |
| 403  | `detail.code === "MUST_CHANGE_PASSWORD"`      | ต้องเปลี่ยน password | ดูหัวข้อ 3.2                       |

---

### 3.2 กรณี MUST_CHANGE_PASSWORD (403)

เมื่อ admin สร้าง account ให้ → login ครั้งแรกจะได้ 403 นี้:

```json
{
  "detail": {
    "code": "MUST_CHANGE_PASSWORD",
    "tempToken": "eyJ...",
    "message": "You must change your password to continue."
  }
}
```

**Flow:**

1. ดัก `status === 403` และ `detail.code === "MUST_CHANGE_PASSWORD"`
2. นำ user ไปหน้า "ตั้งรหัสผ่านใหม่"
3. เรียก `POST /auth/change-password` โดยใช้ `tempToken` เป็น Bearer token:

```
POST /auth/change-password
Authorization: Bearer <tempToken>
```

```json
{
  "oldPassword": "รหัสเดิมที่ได้รับจาก admin",
  "newPassword": "รหัสใหม่ที่ต้องการ"
}
```

4. สำเร็จ → login ใหม่ด้วย password ใหม่ตามปกติ

---

### 3.3 Protected Requests

ทุก endpoint ที่ต้อง login ให้ส่ง header:

```
Authorization: Bearer <accessToken>
```

---

### 3.4 Refresh Token

`accessToken` หมดอายุใน **1 ชั่วโมง** — เมื่อได้ 401 ให้ขอใหม่:

```
POST /auth/refresh
```

```json
{
  "refreshToken": "eyJ..."
}
```

**Response (200)**

```json
{
  "accessToken": "eyJ...(ใหม่)",
  "refreshToken": "eyJ...(ใหม่)"
}
```

> ⚠️ `refreshToken` จะถูก **rotate** ทุกครั้ง — ต้องอัปเดต token ที่เก็บไว้ด้วย

**`refreshToken` หมดอายุใน 30 วัน (staging) / 7 วัน (production)** — ถ้าได้ 401 ต้องให้ user login ใหม่

---

### 3.5 Logout

```
POST /auth/logout
```

```json
{
  "refreshToken": "eyJ..."
}
```

Response 200:

```json
{ "message": "Logged out successfully" }
```

---

## 4. Password Rules

password ที่ใช้ลงทะเบียน / เปลี่ยนรหัส ต้องผ่านเงื่อนไขทั้งหมด:

- ความยาวอย่างน้อย **8 ตัวอักษร**
- มีตัวพิมพ์ใหญ่ (A–Z) **อย่างน้อย 1 ตัว**
- มีตัวพิมพ์เล็ก (a–z) **อย่างน้อย 1 ตัว**
- มีตัวเลข (0–9) **อย่างน้อย 1 ตัว**
- มีอักขระพิเศษ (`@`, `#`, `!`, `$`, ฯลฯ) **อย่างน้อย 1 ตัว**

ถ้าไม่ผ่านจะได้ HTTP 422 พร้อม validation error

---

## 5. Token Storage

| Platform | วิธีแนะนำ                                                                            |
| -------- | ------------------------------------------------------------------------------------ |
| Flutter  | `flutter_secure_storage`                                                             |
| Web      | `httpOnly cookie` หรือ `sessionStorage` (ห้ามใช้ `localStorage` สำหรับ refreshToken) |

---

## 6. Rate Limits

| Endpoint             | ขีดจำกัด                   |
| -------------------- | -------------------------- |
| `POST /auth/login`   | **10 ครั้ง / นาที** ต่อ IP |
| `POST /auth/refresh` | **20 ครั้ง / นาที** ต่อ IP |

เกินขีดจำกัด → HTTP 429 `Too Many Requests`

---

## 7. Signup (สมัครสมาชิกเอง)

```
POST /auth/signup
```

```json
{
  "email": "user@example.com",
  "username": "user01",
  "firstName": "สมชาย",
  "lastName": "ใจดี",
  "password": "MyPass@123"
}
```

Response 201:

```json
{
  "message": "Account created successfully. Please wait for admin approval.",
  "userId": "uuid"
}
```

> account จะอยู่ในสถานะ **PENDING** รอ admin อนุมัติก่อน login ได้

---

## 8. ตัวอย่าง Dart (Flutter)

```dart
// lib/services/auth_service.dart

static const _baseUrl = 'http://10.0.2.2:2531/api'; // Android Emulator

Future<AuthResponse> login(String email, String password) async {
  final res = await http.post(
    Uri.parse('$_baseUrl/auth/login'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({'email': email, 'password': password}),
  );

  if (res.statusCode == 200) {
    return AuthResponse.fromJson(jsonDecode(res.body));
  }

  final body = jsonDecode(res.body);

  // Handle force change password
  if (res.statusCode == 403 && body['detail']?['code'] == 'MUST_CHANGE_PASSWORD') {
    throw MustChangePasswordException(tempToken: body['detail']['tempToken']);
  }

  throw ApiException(body['detail'] ?? 'Login failed');
}

Future<TokenPair> refreshToken(String refreshToken) async {
  final res = await http.post(
    Uri.parse('$_baseUrl/auth/refresh'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({'refreshToken': refreshToken}),
  );
  if (res.statusCode == 200) return TokenPair.fromJson(jsonDecode(res.body));
  throw ApiException('Session expired. Please login again.');
}
```
