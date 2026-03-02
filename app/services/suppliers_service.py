from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rubber_type import RubberType
from app.models.supplier import Supplier
from app.schemas.supplier import CreateSupplierDto, UpdateSupplierDto


class SuppliersService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, payload: CreateSupplierDto) -> dict:
        supplier = Supplier(
            id=str(uuid4()),
            code=payload.code,
            name=payload.name,
            first_name=payload.firstName,
            last_name=payload.lastName,
            title=payload.title,
            tax_id=payload.taxId,
            address=payload.address,
            phone=payload.phone,
            email=str(payload.email) if payload.email else None,
            status=payload.status or "ACTIVE",
            avatar=payload.avatar,
            zip_code=payload.zipCode,
            certificate_number=payload.certificateNumber,
            certificate_expire=payload.certificateExpire,
            score=payload.score,
            eudr_quota_used=payload.eudrQuotaUsed,
            eudr_quota_current=payload.eudrQuotaCurrent,
            rubber_type_codes=payload.rubberTypeCodes or [],
            notes=payload.notes,
            province_id=payload.provinceId,
            district_id=payload.districtId,
            subdistrict_id=payload.subdistrictId,
        )
        self.db.add(supplier)
        await self.db.commit()
        await self.db.refresh(supplier)
        return await self._serialize_supplier(supplier)

    async def find_all(self, include_deleted: bool = False) -> list[dict]:
        query = select(Supplier).order_by(desc(Supplier.created_at))
        if not include_deleted:
            query = query.where(Supplier.deleted_at.is_(None))

        result = await self.db.execute(query)
        suppliers = result.scalars().all()
        return [await self._serialize_supplier(item) for item in suppliers]

    async def find_one(self, supplier_id: str) -> dict:
        supplier = await self.db.get(Supplier, supplier_id)
        if not supplier:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
        return await self._serialize_supplier(supplier)

    async def update(self, supplier_id: str, payload: UpdateSupplierDto) -> dict:
        supplier = await self.db.get(Supplier, supplier_id)
        if not supplier:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")

        data = payload.model_dump(exclude_unset=True)
        field_map = {
            "firstName": "first_name",
            "lastName": "last_name",
            "taxId": "tax_id",
            "zipCode": "zip_code",
            "certificateNumber": "certificate_number",
            "certificateExpire": "certificate_expire",
            "eudrQuotaUsed": "eudr_quota_used",
            "eudrQuotaCurrent": "eudr_quota_current",
            "rubberTypeCodes": "rubber_type_codes",
            "provinceId": "province_id",
            "districtId": "district_id",
            "subdistrictId": "subdistrict_id",
        }

        for key, value in data.items():
            target = field_map.get(key, key)
            if target == "email" and value is not None:
                value = str(value)
            if hasattr(supplier, target):
                setattr(supplier, target, value)

        await self.db.commit()
        await self.db.refresh(supplier)
        return await self._serialize_supplier(supplier)

    async def remove(self, supplier_id: str) -> dict:
        supplier = await self.db.get(Supplier, supplier_id)
        if not supplier:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")

        data = await self._serialize_supplier(supplier)
        await self.db.delete(supplier)
        await self.db.commit()
        return data

    async def soft_delete(self, supplier_id: str, user_id: str) -> dict:
        supplier = await self.db.get(Supplier, supplier_id)
        if not supplier:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")

        supplier.deleted_at = datetime.utcnow()
        supplier.deleted_by = user_id
        await self.db.commit()
        await self.db.refresh(supplier)
        return await self._serialize_supplier(supplier)

    async def restore(self, supplier_id: str) -> dict:
        supplier = await self.db.get(Supplier, supplier_id)
        if not supplier:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")

        supplier.deleted_at = None
        supplier.deleted_by = None
        await self.db.commit()
        await self.db.refresh(supplier)
        return await self._serialize_supplier(supplier)

    async def _serialize_supplier(self, supplier: Supplier) -> dict:
        rubber_details = []
        if supplier.rubber_type_codes:
            result = await self.db.execute(select(RubberType).where(RubberType.code.in_(supplier.rubber_type_codes)))
            rubber_map = {row.code: row for row in result.scalars().all()}
            for code in supplier.rubber_type_codes:
                item = rubber_map.get(code)
                rubber_details.append(
                    {
                        "code": code,
                        "name": item.name if item else code,
                        "category": item.category if item and item.category else "Other",
                    }
                )

        return {
            "id": supplier.id,
            "code": supplier.code,
            "name": supplier.name,
            "firstName": supplier.first_name,
            "lastName": supplier.last_name,
            "title": supplier.title,
            "taxId": supplier.tax_id,
            "address": supplier.address,
            "phone": supplier.phone,
            "email": supplier.email,
            "status": supplier.status,
            "avatar": supplier.avatar,
            "zipCode": supplier.zip_code,
            "certificateNumber": supplier.certificate_number,
            "certificateExpire": supplier.certificate_expire,
            "score": supplier.score,
            "eudrQuotaUsed": supplier.eudr_quota_used,
            "eudrQuotaCurrent": supplier.eudr_quota_current,
            "rubberTypeCodes": supplier.rubber_type_codes,
            "rubberTypeDetails": rubber_details,
            "notes": supplier.notes,
            "provinceId": supplier.province_id,
            "districtId": supplier.district_id,
            "subdistrictId": supplier.subdistrict_id,
            "province": {
                "id": supplier.province.id,
                "code": supplier.province.code,
                "name_th": supplier.province.name_th,
                "name_en": supplier.province.name_en,
            }
            if supplier.province
            else None,
            "district": {
                "id": supplier.district.id,
                "code": supplier.district.code,
                "name_th": supplier.district.name_th,
                "name_en": supplier.district.name_en,
            }
            if supplier.district
            else None,
            "subdistrict": {
                "id": supplier.subdistrict.id,
                "code": supplier.subdistrict.code,
                "name_th": supplier.subdistrict.name_th,
                "name_en": supplier.subdistrict.name_en,
                "zip_code": supplier.subdistrict.zip_code,
            }
            if supplier.subdistrict
            else None,
            "deletedAt": supplier.deleted_at,
            "deletedBy": supplier.deleted_by,
            "createdAt": supplier.created_at,
            "updatedAt": supplier.updated_at,
        }
