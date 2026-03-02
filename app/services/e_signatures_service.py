from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.e_signature import ESignature
from app.schemas.e_signature import CreateESignatureDto, UpdateESignatureDto


class ESignaturesService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, payload: CreateESignatureDto) -> dict:
        data = payload.model_dump()
        if data.get("status") is not False:
            await self.db.execute(
                select(ESignature)
                .where(ESignature.employee_id == data["employeeId"])
                .execution_options(synchronize_session=False)
            )
            result = await self.db.execute(select(ESignature).where(ESignature.employee_id == data["employeeId"]))
            for sig in result.scalars().all():
                sig.status = False

        signature = ESignature(
            id=str(uuid4()),
            employee_id=data["employeeId"],
            signature=data["signature"],
            status=data.get("status", True),
        )
        self.db.add(signature)
        await self.db.commit()
        await self.db.refresh(signature)
        return self._serialize(signature)

    async def find_all(self) -> list[dict]:
        result = await self.db.execute(select(ESignature).order_by(desc(ESignature.created_at)))
        return [self._serialize(item) for item in result.scalars().all()]

    async def find_one(self, signature_id: str) -> dict:
        signature = await self.db.get(ESignature, signature_id)
        if not signature:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="E-Signature not found")
        return self._serialize(signature)

    async def find_by_employee_id(self, employee_id: str) -> list[dict]:
        result = await self.db.execute(
            select(ESignature).where(ESignature.employee_id == employee_id).order_by(desc(ESignature.created_at))
        )
        return [self._serialize(item) for item in result.scalars().all()]

    async def get_active_by_employee_id(self, employee_id: str) -> dict:
        result = await self.db.execute(
            select(ESignature)
            .where(ESignature.employee_id == employee_id, ESignature.status == True)
            .order_by(desc(ESignature.created_at))
            .limit(1)
        )
        signature = result.scalar_one_or_none()
        if not signature:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Active E-Signature for employee {employee_id} not found",
            )
        return self._serialize(signature)

    async def update(self, signature_id: str, payload: UpdateESignatureDto) -> dict:
        signature = await self.db.get(ESignature, signature_id)
        if not signature:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="E-Signature not found")

        data = payload.model_dump(exclude_unset=True)
        if data.get("status") is True:
            result = await self.db.execute(
                select(ESignature).where(ESignature.employee_id == signature.employee_id, ESignature.id != signature_id)
            )
            for sig in result.scalars().all():
                sig.status = False

        for key, value in data.items():
            target = "employee_id" if key == "employeeId" else key
            if hasattr(signature, target):
                setattr(signature, target, value)

        await self.db.commit()
        await self.db.refresh(signature)
        return self._serialize(signature)

    async def remove(self, signature_id: str) -> dict:
        signature = await self.db.get(ESignature, signature_id)
        if not signature:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="E-Signature not found")
        data = {"id": signature.id, "employeeId": signature.employee_id}
        await self.db.delete(signature)
        await self.db.commit()
        return data

    def _serialize(self, signature: ESignature) -> dict:
        return {
            "id": signature.id,
            "employeeId": signature.employee_id,
            "signature": signature.signature,
            "status": signature.status,
            "createdAt": signature.created_at,
            "updatedAt": signature.updated_at,
        }
