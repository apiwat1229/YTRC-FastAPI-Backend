# YTRC Center API — Deployment & Operations Guide

## สารบัญ

1. [โครงสร้างระบบ](#1-โครงสร้างระบบ)
2. [Environment ที่มี](#2-environment-ที่มี)
3. [การรันระบบ](#3-การรันระบบ)
4. [Workflow การพัฒนา](#4-workflow-การพัฒนา)
5. [การแก้ไข Code แล้ว Deploy](#5-การแก้ไข-code-แล้ว-deploy)
6. [คำสั่งที่ใช้บ่อย](#6-คำสั่งที่ใช้บ่อย)
7. [โครงสร้างไฟล์ Config](#7-โครงสร้างไฟล์-config)
8. [ข้อควรระวัง](#8-ข้อควรระวัง)

---

## 1. โครงสร้างระบบ

ระบบใช้ **Docker Compose Override** แยก environment ออกจากกันสมบูรณ์:

```
┌─────────────────────────────────┐   ┌─────────────────────────────────┐
│         PRODUCTION               │   │           STAGING                │
│  Project: ytrc-prod              │   │  Project: ytrc-staging           │
│                                  │   │                                  │
│  API   → port 2530               │   │  API    → port 2531              │
│  DB    → port 5433               │   │  DB     → port 5434              │
│  Admin → port 5050               │   │  Admin  → port 5051              │
│                                  │   │                                  │
│  DB: myapp                       │   │  DB: myapp_staging               │
│  ENVIRONMENT=production          │   │  ENVIRONMENT=staging             │
│  /docs → ❌ ปิด                  │   │  /docs  → ✅ เปิด               │
│  log-level: warning              │   │  log-level: debug                │
│  JWT: 1h                         │   │  JWT: 8h                         │
└─────────────────────────────────┘   └─────────────────────────────────┘
         ↑ ข้อมูลจริง                           ↑ ข้อมูลทดสอบ
         ❌ ห้ามเขียนทดลอง                      ✅ ทดลองได้เต็มที่
```

**ทั้งสองรันพร้อมกันบน server เดียวกันได้** เพราะ port, volume, container name แยกกันทั้งหมด

---

## 2. Environment ที่มี

|                      | Production                 | Staging                      |
| -------------------- | -------------------------- | ---------------------------- |
| **คำสั่ง project**   | `-p ytrc-prod`             | `-p ytrc-staging`            |
| **Compose override** | `docker-compose.prod.yml`  | `docker-compose.staging.yml` |
| **Env file**         | `.env.production`          | `.env.staging`               |
| **API URL**          | `http://server:2530/api`   | `http://server:2531/api`     |
| **Swagger Docs**     | ปิด (404)                  | เปิด `/docs`                 |
| **DB name**          | `myapp`                    | `myapp_staging`              |
| **JWT หมดอายุ**      | Access 1h / Refresh 7d     | Access 8h / Refresh 30d      |
| **CORS**             | production domain เท่านั้น | localhost + ทุก origin dev   |
| **restart policy**   | `always`                   | `unless-stopped`             |

---

## 3. การรันระบบ

### ▶️ รัน Production

```bash
docker-compose -p ytrc-prod \
  -f docker-compose.yml \
  -f docker-compose.prod.yml \
  --env-file .env.production \
  up -d --build
```

### ▶️ รัน Staging

```bash
docker-compose -p ytrc-staging \
  -f docker-compose.yml \
  -f docker-compose.staging.yml \
  --env-file .env.staging \
  up -d --build
```

> **`--build`** — บังคับ build image ใหม่ทุกครั้ง ต้องใส่เสมอเมื่อมีการแก้ไข code  
> ถ้าแค่ restart โดยไม่แก้ code ใส่แค่ `up -d` ได้

### ⏹️ หยุด Production

```bash
docker-compose -p ytrc-prod \
  -f docker-compose.yml \
  -f docker-compose.prod.yml \
  down
```

### ⏹️ หยุด Staging

```bash
docker-compose -p ytrc-staging \
  -f docker-compose.yml \
  -f docker-compose.staging.yml \
  down
```

### ⏹️ หยุดแล้ว Reset DB Staging (ลบข้อมูลทั้งหมด)

```bash
docker-compose -p ytrc-staging \
  -f docker-compose.yml \
  -f docker-compose.staging.yml \
  down -v
```

> ⚠️ **อย่าใช้ `-v` กับ production เด็ดขาด** — จะลบ volume ข้อมูลจริงทิ้งทั้งหมด

---

## 4. Workflow การพัฒนา

```
          Developer Machine
          ─────────────────
          1. แก้ไข code
          2. git commit & push
                  │
                  ▼
          Server (Staging)
          ─────────────────
          3. git pull
          4. docker-compose ... staging up -d --build
          5. ทดสอบที่ http://server:2531
          6. เขียน/แก้ไขข้อมูลทดสอบได้เต็มที่
                  │
           ✅ ผ่านทุกอย่าง?
                  │
                  ▼
          Server (Production)
          ───────────────────
          7. docker-compose ... prod up -d --build
          8. ตรวจสอบ health ที่ http://server:2530/api/health
```

---

## 5. การแก้ไข Code แล้ว Deploy

### ขั้นที่ 1 — บน Developer Machine

```bash
# แก้ไข code ตามต้องการ

# Commit และ Push
git add .
git commit -m "feat: อธิบายสิ่งที่เปลี่ยน"
git push origin main
```

### ขั้นที่ 2 — Deploy Staging ก่อน

```bash
# Pull code ล่าสุด
git pull origin main

# Build และรัน staging ใหม่
docker-compose -p ytrc-staging \
  -f docker-compose.yml \
  -f docker-compose.staging.yml \
  --env-file .env.staging \
  up -d --build

# ดู log ว่า startup ปกติ
docker logs ytrc-staging-api -f
```

เปิด `http://server:2531/docs` ทดสอบ API ได้เลย

### ขั้นที่ 3 — Deploy Production หลังทดสอบผ่าน

```bash
# Build และรัน production ใหม่
docker-compose -p ytrc-prod \
  -f docker-compose.yml \
  -f docker-compose.prod.yml \
  --env-file .env.production \
  up -d --build

# ตรวจสอบ health
curl http://localhost:2530/api/health
```

---

## 6. คำสั่งที่ใช้บ่อย

### ดูสถานะ Containers ทั้งหมด

```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### ดู Log แบบ Real-time

```bash
# Production
docker logs ytrc-fastapi-api -f

# Staging
docker logs ytrc-staging-api -f

# เฉพาะ 50 บรรทัดล่าสุด
docker logs ytrc-fastapi-api --tail 50
```

### Restart เฉพาะ API (ไม่ต้อง build ใหม่)

```bash
# Production
docker restart ytrc-fastapi-api

# Staging
docker restart ytrc-staging-api
```

### ตรวจสอบ Health

```bash
# Production
curl http://localhost:2530/api/health

# Staging
curl http://localhost:2531/api/health
```

### เข้า psql ใน Container

```bash
# Production DB
docker exec -it ytrc-fastapi-db psql -U postgres -d myapp

# Staging DB
docker exec -it ytrc-staging-db psql -U postgres -d myapp_staging

# คำสั่ง psql ที่ใช้บ่อย
\dt          -- แสดงตารางทั้งหมด
\d users     -- ดู schema ของตาราง
\q           -- ออก
```

### Rebuild เฉพาะ API Image (ไม่แตะ DB)

```bash
# Production
docker-compose -p ytrc-prod \
  -f docker-compose.yml -f docker-compose.prod.yml \
  --env-file .env.production \
  up -d --build api

# Staging
docker-compose -p ytrc-staging \
  -f docker-compose.yml -f docker-compose.staging.yml \
  --env-file .env.staging \
  up -d --build api
```

---

## 7. โครงสร้างไฟล์ Config

```
BackEnd-FastAPI/
├── docker-compose.yml              ← Base config (shared โครงกระดูก)
├── docker-compose.staging.yml      ← Staging override (port, container name)
├── docker-compose.prod.yml         ← Production override (restart, memory limit)
│
├── .env.staging                    ← Environment variables สำหรับ staging
├── .env.production                 ← Environment variables สำหรับ production ⚠️
├── .env.docker                     ← Legacy (standalone ไม่แยก env)
│
├── .gitignore                      ← ignore .env.staging, .env.production
└── app/
    ├── main.py                     ← ปิด /docs อัตโนมัติเมื่อ ENVIRONMENT=production
    └── core/
        └── config.py               ← JWT_SECRET ไม่มี default (required)
```

### ค่าสำคัญที่ต้องแก้ก่อน Deploy Production จริง

เปิดไฟล์ `.env.production` แล้วแก้ค่าเหล่านี้:

```dotenv
# เปลี่ยน password DB ให้แข็งแรง
POSTGRES_PASSWORD=ใส่_password_ที่ซับซ้อน
DATABASE_URL=postgresql+asyncpg://postgres:ใส่_password_ที่ซับซ้อน@db:5432/myapp

# เปลี่ยน JWT secret ให้ยาวอย่างน้อย 32 ตัวอักษร
JWT_SECRET=random_string_ยาวๆ_อย่างน้อย_32_ตัวอักษร

# ใส่ domain จริงของระบบ
CORS_ORIGINS=https://your-production-domain.com

# เปลี่ยน pgAdmin credentials
PGADMIN_EMAIL=it@company.com
PGADMIN_PASSWORD=strong_password
```

---

## 8. ข้อควรระวัง

### 🔴 ห้ามทำ

| สิ่งที่ห้ามทำ                                          | เหตุผล                               |
| ------------------------------------------------------ | ------------------------------------ |
| `docker-compose ... down -v` บน production             | ลบ volume = ลบข้อมูลจริงทั้งหมด      |
| Commit `.env.production` ขึ้น Git                      | มี password และ secret จริง          |
| แก้ schema ตาราง production โดยไม่ทดสอบบน staging ก่อน | ข้อมูลจริงอาจเสียหาย                 |
| ใช้ JWT_SECRET เดียวกันระหว่าง staging และ production  | Token staging จะใช้บน production ได้ |

### 🟡 ควรทำ

| สิ่งที่ควรทำ                                              | เหตุผล                                                               |
| --------------------------------------------------------- | -------------------------------------------------------------------- |
| ทดสอบบน staging ก่อนทุกครั้ง                              | ป้องกัน bug ใน production                                            |
| Backup DB ก่อน deploy production                          | `docker exec ytrc-fastapi-db pg_dump -U postgres myapp > backup.sql` |
| ตรวจ `docker logs` หลัง deploy ทุกครั้ง                   | ตรวจสอบว่า startup ไม่มี error                                       |
| เปลี่ยน JWT_SECRET และ POSTGRES_PASSWORD ก่อน deploy จริง | ความปลอดภัย                                                          |

---

## ตาราง URLs สรุป

| Service          | Production                      | Staging                         |
| ---------------- | ------------------------------- | ------------------------------- |
| **API**          | `http://server:2530/api`        | `http://server:2531/api`        |
| **Health Check** | `http://server:2530/api/health` | `http://server:2531/api/health` |
| **Swagger Docs** | ❌ ปิด                          | `http://server:2531/docs`       |
| **pgAdmin**      | `http://server:5050`            | `http://server:5051`            |
| **DB (psql)**    | port `5433`                     | port `5434`                     |
