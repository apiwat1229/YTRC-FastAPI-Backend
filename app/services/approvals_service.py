from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import String, and_, cast, desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.approval_log import ApprovalLog
from app.models.approval_request import ApprovalRequest
from app.models.booking import Booking
from app.models.rubber_type import RubberType
from app.models.supplier import Supplier
from app.models.user import User
from app.schemas.approval import (ApproveDto, CancelDto,
                                  CreateApprovalRequestDto, RejectDto,
                                  ReturnDto, VoidDto)
from app.services.notifications_service import NotificationsService


class ApprovalsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.notifications = NotificationsService(db)

    async def create_request(self, requester_id: str, dto: CreateApprovalRequestDto) -> dict:
        requester = await self.db.get(User, requester_id)
        if not requester:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requester not found")

        request = ApprovalRequest(
            id=str(uuid4()),
            request_type=dto.requestType,
            entity_type=dto.entityType,
            entity_id=dto.entityId,
            source_app=dto.sourceApp,
            action_type=dto.actionType,
            current_data=dto.currentData or {},
            proposed_data=dto.proposedData or {},
            reason=dto.reason,
            priority=dto.priority or "NORMAL",
            expires_at=dto.expiresAt,
            requester_id=requester_id,
            status="PENDING",
        )
        self.db.add(request)
        await self.db.commit()
        await self.db.refresh(request)

        await self._create_audit_log(
            approval_request_id=request.id,
            action="CREATED",
            actor_id=requester_id,
            actor_name=requester.display_name or requester.email,
            actor_role=requester.role,
            new_value={"status": "PENDING"},
            remark=dto.reason,
        )

        await self._notify_approvers(request, requester)
        return await self.find_one(request.id)

    async def find_all(self, status_filter: str | None, entity_type: str | None, include_deleted: bool) -> list[dict]:
        query = select(ApprovalRequest)
        if status_filter:
            query = query.where(cast(ApprovalRequest.status, String) == status_filter)
        if entity_type:
            query = query.where(ApprovalRequest.entity_type == entity_type)
        if not include_deleted:
            query = query.where(ApprovalRequest.deleted_at.is_(None))

        query = query.order_by(desc(ApprovalRequest.submitted_at))
        result = await self.db.execute(query)
        return [await self._serialize_request(item) for item in result.scalars().all()]

    async def find_one(self, request_id: str) -> dict:
        request = await self.db.get(ApprovalRequest, request_id)
        if not request:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval request not found")
        return await self._serialize_request(request)

    async def find_my_requests(self, user_id: str) -> list[dict]:
        result = await self.db.execute(
            select(ApprovalRequest)
            .where(and_(ApprovalRequest.requester_id == user_id, ApprovalRequest.deleted_at.is_(None)))
            .order_by(desc(ApprovalRequest.submitted_at))
        )
        return [await self._serialize_request(item) for item in result.scalars().all()]

    async def approve(self, request_id: str, approver_id: str, dto: ApproveDto) -> dict:
        request = await self._get_pending_request(request_id)
        approver = await self._require_user(approver_id)

        request.status = "APPROVED"
        request.approver_id = approver_id
        request.acted_at = datetime.utcnow()
        request.remark = dto.remark
        await self.db.commit()

        await self._create_audit_log(
            approval_request_id=request.id,
            action="APPROVED",
            actor_id=approver_id,
            actor_name=approver.display_name or approver.email,
            actor_role=approver.role,
            old_value={"status": "PENDING"},
            new_value={"status": "APPROVED"},
            remark=dto.remark,
        )

        await self.notifications.create(
            {
                "userId": request.requester_id,
                "title": "คำขออนุมัติได้รับการอนุมัติ",
                "message": f"คำขอ {request.request_type} ของคุณได้รับการอนุมัติแล้ว",
                "type": "APPROVE",
                "sourceApp": "APPROVALS",
                "actionType": "APPROVED",
                "entityId": request.id,
                "actionUrl": f"/approvals/{request.id}",
            }
        )

        await self._apply_approved_changes(request)
        return await self.find_one(request.id)

    async def reject(self, request_id: str, approver_id: str, dto: RejectDto) -> dict:
        request = await self._get_pending_request(request_id)
        approver = await self._require_user(approver_id)

        request.status = "REJECTED"
        request.approver_id = approver_id
        request.acted_at = datetime.utcnow()
        request.remark = dto.remark
        await self.db.commit()

        await self._create_audit_log(
            approval_request_id=request.id,
            action="REJECTED",
            actor_id=approver_id,
            actor_name=approver.display_name or approver.email,
            actor_role=approver.role,
            old_value={"status": "PENDING"},
            new_value={"status": "REJECTED"},
            remark=dto.remark,
        )

        await self.notifications.create(
            {
                "userId": request.requester_id,
                "title": "คำขออนุมัติถูกปฏิเสธ",
                "message": f"คำขอ {request.request_type} ถูกปฏิเสธ: {dto.remark}",
                "type": "ERROR",
                "sourceApp": "APPROVALS",
                "actionType": "REJECTED",
                "entityId": request.id,
                "actionUrl": f"/approvals/{request.id}",
            }
        )

        return await self.find_one(request.id)

    async def return_for_modification(self, request_id: str, approver_id: str, dto: ReturnDto) -> dict:
        request = await self._get_pending_request(request_id)
        approver = await self._require_user(approver_id)

        request.status = "RETURNED"
        request.approver_id = approver_id
        request.acted_at = datetime.utcnow()
        request.remark = dto.remark
        await self.db.commit()

        await self._create_audit_log(
            approval_request_id=request.id,
            action="RETURNED",
            actor_id=approver_id,
            actor_name=approver.display_name or approver.email,
            actor_role=approver.role,
            old_value={"status": "PENDING"},
            new_value={"status": "RETURNED"},
            remark=dto.remark,
        )

        await self.notifications.create(
            {
                "userId": request.requester_id,
                "title": "คำขอถูกส่งคืนเพื่อแก้ไข",
                "message": f"คำขอ {request.request_type} ถูกส่งคืน: {dto.remark}",
                "type": "WARNING",
                "sourceApp": "APPROVALS",
                "actionType": "RETURNED",
                "entityId": request.id,
                "actionUrl": f"/approvals/{request.id}",
            }
        )

        return await self.find_one(request.id)

    async def cancel(self, request_id: str, user_id: str, dto: CancelDto) -> dict:
        request = await self.db.get(ApprovalRequest, request_id)
        if not request:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval request not found")
        if request.requester_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the requester can cancel this request")
        if request.status != "PENDING":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only pending requests can be cancelled")

        user = await self._require_user(user_id)
        request.status = "CANCELLED"
        request.acted_at = datetime.utcnow()
        request.remark = dto.reason
        await self.db.commit()

        await self._create_audit_log(
            approval_request_id=request.id,
            action="CANCELLED",
            actor_id=user_id,
            actor_name=user.display_name or user.email,
            actor_role=user.role,
            old_value={"status": "PENDING"},
            new_value={"status": "CANCELLED"},
            remark=dto.reason,
        )

        return await self.find_one(request.id)

    async def void(self, request_id: str, admin_id: str, dto: VoidDto) -> dict:
        request = await self.db.get(ApprovalRequest, request_id)
        if not request:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval request not found")
        if request.status != "APPROVED":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only approved requests can be voided")

        admin = await self._require_user(admin_id)
        request.status = "VOID"
        request.acted_at = datetime.utcnow()
        request.remark = dto.reason
        await self.db.commit()

        await self._create_audit_log(
            approval_request_id=request.id,
            action="VOIDED",
            actor_id=admin_id,
            actor_name=admin.display_name or admin.email,
            actor_role=admin.role,
            old_value={"status": "APPROVED"},
            new_value={"status": "VOID"},
            remark=dto.reason,
        )

        await self.notifications.create(
            {
                "userId": request.requester_id,
                "title": "คำขอถูกทำเป็นโมฆะ",
                "message": f"คำขอ {request.request_type} ที่อนุมัติแล้วถูกทำเป็นโมฆะ: {dto.reason}",
                "type": "WARNING",
                "sourceApp": "APPROVALS",
                "actionType": "VOIDED",
                "entityId": request.id,
                "actionUrl": f"/approvals/{request.id}",
            }
        )

        return await self.find_one(request.id)

    async def soft_delete(self, request_id: str, user_id: str) -> dict:
        request = await self.db.get(ApprovalRequest, request_id)
        if not request:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval request not found")

        user = await self._require_user(user_id)
        request.deleted_at = datetime.utcnow()
        request.deleted_by = user_id
        await self.db.commit()

        await self._create_audit_log(
            approval_request_id=request.id,
            action="DELETED",
            actor_id=user_id,
            actor_name=user.display_name or user.email,
            actor_role=user.role,
            old_value={"deletedAt": None},
            new_value={"deletedAt": request.deleted_at.isoformat()},
        )

        return await self.find_one(request.id)

    async def get_history(self, request_id: str) -> list[dict]:
        _ = await self.find_one(request_id)
        result = await self.db.execute(
            select(ApprovalLog).where(ApprovalLog.approval_request_id == request_id).order_by(ApprovalLog.created_at.asc())
        )
        return [self._serialize_log(item) for item in result.scalars().all()]

    async def _apply_approved_changes(self, request: ApprovalRequest) -> None:
        entity = (request.entity_type or "").upper()
        action = (request.action_type or "").upper()
        data = request.proposed_data or {}

        try:
            if action in {"UPDATE", "EDIT_WEIGHT_IN"}:
                if entity == "SUPPLIER":
                    target = await self.db.get(Supplier, request.entity_id)
                    if target:
                        for key, value in self._map_supplier_data(data).items():
                            if hasattr(target, key):
                                setattr(target, key, value)
                elif entity == "RUBBERTYPE":
                    target = await self.db.get(RubberType, request.entity_id)
                    if target:
                        for key, value in self._map_rubber_type_data(data).items():
                            if hasattr(target, key):
                                setattr(target, key, value)
                elif entity == "BOOKING":
                    target = await self.db.get(Booking, request.entity_id)
                    if target:
                        for key, value in self._map_booking_data(data).items():
                            if hasattr(target, key):
                                setattr(target, key, value)
            elif action == "DELETE":
                if entity == "SUPPLIER":
                    target = await self.db.get(Supplier, request.entity_id)
                    if target:
                        target.deleted_at = datetime.utcnow()
                        target.deleted_by = request.approver_id
                elif entity == "RUBBERTYPE":
                    target = await self.db.get(RubberType, request.entity_id)
                    if target:
                        target.deleted_at = datetime.utcnow()
                        target.deleted_by = request.approver_id
                elif entity == "BOOKING":
                    target = await self.db.get(Booking, request.entity_id)
                    if target:
                        target.deleted_at = datetime.utcnow()
                        target.deleted_by = request.approver_id
                        target.status = "CANCELLED"
            await self.db.commit()
        except Exception:
            await self.db.rollback()

    async def _create_audit_log(
        self,
        approval_request_id: str,
        action: str,
        actor_id: str,
        actor_name: str,
        actor_role: str,
        old_value=None,
        new_value=None,
        remark: str | None = None,
    ) -> None:
        log = ApprovalLog(
            id=str(uuid4()),
            approval_request_id=approval_request_id,
            action=action,
            actor_id=actor_id,
            actor_name=actor_name,
            actor_role=actor_role,
            old_value=old_value or {},
            new_value=new_value or {},
            remark=remark,
        )
        self.db.add(log)
        await self.db.commit()

    async def _notify_approvers(self, request: ApprovalRequest, requester: User) -> None:
        result = await self.db.execute(
            select(User).where(and_(User.role.in_(["ADMIN", "admin"]), User.status == "ACTIVE"))
        )
        admins = result.scalars().all()
        for admin in admins:
            await self.notifications.create(
                {
                    "userId": admin.id,
                    "title": "คำขออนุมัติใหม่",
                    "message": f"{requester.display_name or requester.email} ส่งคำขอ {request.request_type}",
                    "type": "REQUEST",
                    "sourceApp": "APPROVALS",
                    "actionType": "APPROVAL_REQUEST",
                    "entityId": request.id,
                    "actionUrl": f"/approvals/{request.id}",
                }
            )

    async def _get_pending_request(self, request_id: str) -> ApprovalRequest:
        request = await self.db.get(ApprovalRequest, request_id)
        if not request:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval request not found")
        if request.status != "PENDING":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only pending requests can be processed")
        return request

    async def _require_user(self, user_id: str) -> User:
        user = await self.db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    async def _serialize_request(self, request: ApprovalRequest) -> dict:
        requester = await self.db.get(User, request.requester_id)
        approver = await self.db.get(User, request.approver_id) if request.approver_id else None
        return {
            "id": request.id,
            "requestType": request.request_type,
            "entityType": request.entity_type,
            "entityId": request.entity_id,
            "sourceApp": request.source_app,
            "actionType": request.action_type,
            "currentData": request.current_data,
            "proposedData": request.proposed_data,
            "reason": request.reason,
            "priority": request.priority,
            "status": request.status,
            "requesterId": request.requester_id,
            "approverId": request.approver_id,
            "submittedAt": request.submitted_at,
            "actedAt": request.acted_at,
            "expiresAt": request.expires_at,
            "remark": request.remark,
            "deletedAt": request.deleted_at,
            "deletedBy": request.deleted_by,
            "requester": {
                "id": requester.id,
                "displayName": requester.display_name,
                "email": requester.email,
                "role": requester.role,
            }
            if requester
            else None,
            "approver": {
                "id": approver.id,
                "displayName": approver.display_name,
                "email": approver.email,
                "role": approver.role,
            }
            if approver
            else None,
        }

    def _serialize_log(self, item: ApprovalLog) -> dict:
        return {
            "id": item.id,
            "approvalRequestId": item.approval_request_id,
            "action": item.action,
            "oldValue": item.old_value,
            "newValue": item.new_value,
            "actorId": item.actor_id,
            "actorName": item.actor_name,
            "actorRole": item.actor_role,
            "remark": item.remark,
            "ipAddress": item.ip_address,
            "userAgent": item.user_agent,
            "createdAt": item.created_at,
        }

    def _map_supplier_data(self, data: dict) -> dict:
        mapping = {
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
        out = {}
        for key, value in data.items():
            out[mapping.get(key, key)] = value
        return out

    def _map_rubber_type_data(self, data: dict) -> dict:
        out = dict(data)
        if "status" in out:
            out["is_active"] = out.pop("status") == "ACTIVE"
        return out

    def _map_booking_data(self, data: dict) -> dict:
        mapping = {
            "supplierId": "supplier_id",
            "supplierCode": "supplier_code",
            "supplierName": "supplier_name",
            "truckType": "truck_type",
            "truckRegister": "truck_register",
            "rubberType": "rubber_type",
            "estimatedWeight": "estimated_weight",
            "weightIn": "weight_in",
            "weightOut": "weight_out",
            "lotNo": "lot_no",
        }
        out = {}
        for key, value in data.items():
            out[mapping.get(key, key)] = value
        return out

    async def auto_expire_requests(self) -> int:
        now = datetime.utcnow()
        result = await self.db.execute(
            update(ApprovalRequest)
            .where(and_(ApprovalRequest.status == "PENDING", ApprovalRequest.expires_at <= now))
            .values(status="EXPIRED", acted_at=now, remark="Auto-expired by system")
        )
        await self.db.commit()
        return result.rowcount
