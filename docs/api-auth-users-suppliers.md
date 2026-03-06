# API Reference — Auth / Users / Suppliers

**Base URL:** `http://localhost:2530/api`

---

## 🔐 Auth — `/api/auth`

| Method | Endpoint                | Auth Required | หมายเหตุ                                                        |
| ------ | ----------------------- | :-----------: | --------------------------------------------------------------- |
| `POST` | `/auth/login`           |      ❌       | Rate limit **10/นาที** — คืน `accessToken` + `refreshToken`     |
| `POST` | `/auth/signup`          |      ❌       | สมัครสมาชิก → รอ admin อนุมัติ                                  |
| `POST` | `/auth/register`        |      ❌       | สร้าง user แล้ว active ทันที (internal use)                     |
| `POST` | `/auth/refresh`         |      ❌       | Rate limit **20/นาที** — ส่ง `refreshToken` → คืน token คู่ใหม่ |
| `POST` | `/auth/logout`          |      ❌       | ส่ง `refreshToken` → revoke ทันที                               |
| `GET`  | `/auth/me`              |      ✅       | ดึงข้อมูล user ปัจจุบัน + permissions                           |
| `POST` | `/auth/change-password` |      ✅       | เปลี่ยน password (ต้องใส่รหัสเก่า)                              |

### Request Body Examples

```json
// POST /auth/login
{
  "email": "user@example.com",
  "password": "MyPass@123"
}

// POST /auth/signup & /auth/register
{
  "email": "user@example.com",
  "username": "user01",
  "firstName": "สมชาย",
  "lastName": "ใจดี",
  "password": "MyPass@123"
}

// POST /auth/refresh  &  POST /auth/logout
{
  "refreshToken": "eyJ..."
}

// POST /auth/change-password
{
  "oldPassword": "OldPass@123",
  "newPassword": "NewPass@456"
}
```

### Response Example — Login / Register

```json
{
  "accessToken": "eyJ...",
  "refreshToken": "eyJ...",
  "user": {
    "id": "...",
    "email": "user@example.com",
    "username": "user01",
    "displayName": "สมชาย ใจดี",
    "role": "staff_1",
    "permissions": ["suppliers:read", "..."],
    "department": "IT",
    "status": "ACTIVE"
  }
}
```

### Password Rules

- ความยาวขั้นต่ำ **8 ตัวอักษร**
- ต้องมี **ตัวพิมพ์ใหญ่** อย่างน้อย 1 ตัว
- ต้องมี **ตัวพิมพ์เล็ก** อย่างน้อย 1 ตัว
- ต้องมี **ตัวเลข** อย่างน้อย 1 ตัว
- ต้องมี **อักขระพิเศษ** อย่างน้อย 1 ตัว (เช่น `@`, `#`, `!`)

---

## 👤 Users — `/api/users`

> ทุก endpoint ต้อง login ก่อน (`Authorization: Bearer <accessToken>`)

| Method   | Endpoint                              | Permission      |
| -------- | ------------------------------------- | --------------- |
| `POST`   | `/users`                              | `users:create`  |
| `GET`    | `/users`                              | login แล้วก็ได้ |
| `GET`    | `/users/{user_id}`                    | login แล้วก็ได้ |
| `GET`    | `/users/employee/{employeeId}/exists` | login แล้วก็ได้ |
| `PATCH`  | `/users/{user_id}`                    | `users:update`  |
| `PATCH`  | `/users/{user_id}/unlock`             | `users:update`  |
| `DELETE` | `/users/{user_id}`                    | `users:delete`  |
| `POST`   | `/users/{user_id}/avatar`             | `users:update`  |

### Endpoint Descriptions

| Endpoint                                  | คำอธิบาย                                                  |
| ----------------------------------------- | --------------------------------------------------------- |
| `POST /users`                             | สร้าง user ใหม่ (admin สร้างให้)                          |
| `GET /users`                              | ดึง user ทั้งหมด                                          |
| `GET /users/{user_id}`                    | ดึง user ตาม ID                                           |
| `GET /users/employee/{employeeId}/exists` | เช็คว่ามี employee ID นี้ในระบบหรือไม่                    |
| `PATCH /users/{user_id}`                  | แก้ไขข้อมูล user                                          |
| `PATCH /users/{user_id}/unlock`           | ปลดล็อก account ที่ถูกล็อกจาก login ผิดเกิน 5 ครั้ง       |
| `DELETE /users/{user_id}`                 | ลบ user                                                   |
| `POST /users/{user_id}/avatar`            | อัปโหลดรูป profile (`multipart/form-data`, field: `file`) |

---

## 🏭 Suppliers — `/api/suppliers`

> ทุก endpoint ต้อง login ก่อน (`Authorization: Bearer <accessToken>`)

| Method   | Endpoint                         | Permission                 |
| -------- | -------------------------------- | -------------------------- |
| `POST`   | `/suppliers`                     | `suppliers:create`         |
| `GET`    | `/suppliers`                     | `suppliers:read`           |
| `GET`    | `/suppliers/{id}`                | `suppliers:read`           |
| `PATCH`  | `/suppliers/{id}`                | `suppliers:update`         |
| `DELETE` | `/suppliers/{id}`                | `suppliers:delete`         |
| `DELETE` | `/suppliers/{id}/soft`           | `suppliers:delete`         |
| `POST`   | `/suppliers/{id}/restore`        | `suppliers:update`         |
| `POST`   | `/suppliers/{id}/update-request` | `suppliers:update_request` |
| `POST`   | `/suppliers/{id}/delete-request` | `suppliers:delete_request` |

### Endpoint Descriptions

| Endpoint                              | คำอธิบาย                                                                            |
| ------------------------------------- | ----------------------------------------------------------------------------------- |
| `POST /suppliers`                     | สร้าง supplier ใหม่                                                                 |
| `GET /suppliers?includeDeleted=true`  | ดึง supplier ทั้งหมด (เพิ่ม query `includeDeleted=true` เพื่อรวมที่ถูก soft delete) |
| `GET /suppliers/{id}`                 | ดึง supplier ตาม ID                                                                 |
| `PATCH /suppliers/{id}`               | แก้ไข supplier โดยตรง                                                               |
| `DELETE /suppliers/{id}`              | **Hard delete** — ลบถาวร                                                            |
| `DELETE /suppliers/{id}/soft`         | **Soft delete** — ซ่อน แต่ข้อมูลยังอยู่ใน DB                                        |
| `POST /suppliers/{id}/restore`        | กู้คืน supplier ที่ถูก soft delete                                                  |
| `POST /suppliers/{id}/update-request` | ส่งคำขอแก้ไขผ่านระบบ **Approval Workflow**                                          |
| `POST /suppliers/{id}/delete-request` | ส่งคำขอลบผ่านระบบ **Approval Workflow**                                             |

---

## 📌 หมายเหตุทั่วไป

- **Authorization Header:** `Authorization: Bearer <accessToken>`
- **Access Token** หมดอายุใน **1 ชั่วโมง** — ต้องใช้ `/auth/refresh` เพื่อต่ออายุ
- **Refresh Token** หมดอายุใน **7 วัน**
- **ADMIN role** ข้าม permission check ทั้งหมดได้อัตโนมัติ
- Account จะถูกล็อกอัตโนมัติหลัง **login ผิด 5 ครั้ง** — ต้องให้ admin ปลดล็อกผ่าน `PATCH /users/{id}/unlock`
