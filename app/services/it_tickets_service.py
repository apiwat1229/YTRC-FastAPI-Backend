from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.it_asset import ITAsset
from app.models.it_ticket import ITTicket
from app.models.notification_group import NotificationGroup
from app.models.notification_setting import NotificationSetting
from app.models.role import Role
from app.models.ticket_comment import TicketComment
from app.models.user import User
from app.schemas.it_ticket import CreateITTicketDto, CreateTicketCommentDto, UpdateITTicketDto
from app.services.notifications_service import NotificationsService


class ITTicketsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.notifications = NotificationsService(db)

    def _parse_datetime(self, value: str | datetime | None) -> datetime | None:
        if isinstance(value, datetime):
            return value
        if not value:
            return None
        try:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return None

    async def create(self, user_id: str, payload: CreateITTicketDto) -> dict:
        data = payload.model_dump()

        last_result = await self.db.execute(select(ITTicket).order_by(desc(ITTicket.created_at)).limit(1))
        last_ticket = last_result.scalar_one_or_none()

        next_no = 1000
        if last_ticket and last_ticket.ticket_no.startswith("T-"):
            try:
                last_no = int(last_ticket.ticket_no.replace("T-", ""))
                next_no = last_no + 1
            except ValueError:
                pass

        ticket_no = f"T-{next_no}"

        ticket = ITTicket(
            id=str(uuid4()),
            ticket_no=ticket_no,
            title=data["title"],
            description=data.get("description"),
            category=data["category"],
            priority=data.get("priority", "Medium"),
            location=data.get("location"),
            requester_id=user_id,
            is_asset_request=data.get("isAssetRequest", False),
            asset_id=data.get("assetId"),
            quantity=data.get("quantity", 0),
            expected_date=self._parse_datetime(data.get("expectedDate")),
            approver_id=data.get("approverId"),
        )
        if data.get("createdAt"):
            ticket.created_at = self._parse_datetime(data["createdAt"]) or datetime.now()

        self.db.add(ticket)
        await self.db.commit()
        await self.db.refresh(ticket)

        requester = await self.db.get(User, user_id)
        await self._trigger_notification(
            "IT_HELP_DESK",
            "TICKET_CREATED",
            {
                "title": f"New IT Ticket: {ticket.ticket_no}",
                "message": f"{ticket.title} - {requester.display_name if requester else 'Unknown'}",
                "actionUrl": f"/admin/helpdesk?ticketId={ticket.id}",
            },
        )

        if data.get("isAssetRequest") and data.get("approverId"):
            await self._trigger_notification(
                "IT_HELP_DESK",
                "APPROVER_REQUEST",
                {
                    "title": f"Approval Required: {ticket.ticket_no}",
                    "message": f"{requester.display_name if requester else 'Unknown'} requested: {ticket.title}",
                    "actionUrl": f"/admin/helpdesk?ticketId={ticket.id}",
                },
                explicit_user_ids=[data["approverId"]],
                notification_type="REQUEST",
            )

        return await self.find_one(ticket.id)

    async def find_all(self, user_id: str | None, is_admin: bool = False) -> list[dict]:
        query = select(ITTicket)
        if not is_admin and user_id:
            query = query.where(ITTicket.requester_id == user_id)
        query = query.order_by(desc(ITTicket.created_at))

        result = await self.db.execute(query)
        tickets = result.scalars().all()

        output = []
        for ticket in tickets:
            requester = await self.db.get(User, ticket.requester_id)
            assignee = await self.db.get(User, ticket.assignee_id) if ticket.assignee_id else None
            output.append(
                {
                    "id": ticket.id,
                    "ticketNo": ticket.ticket_no,
                    "title": ticket.title,
                    "description": ticket.description,
                    "category": ticket.category,
                    "priority": ticket.priority,
                    "location": ticket.location,
                    "status": ticket.status,
                    "requesterId": ticket.requester_id,
                    "assigneeId": ticket.assignee_id,
                    "isAssetRequest": ticket.is_asset_request,
                    "assetId": ticket.asset_id,
                    "quantity": ticket.quantity,
                    "expectedDate": ticket.expected_date,
                    "approverId": ticket.approver_id,
                    "issuedAt": ticket.issued_at,
                    "issuedBy": ticket.issued_by,
                    "resolvedAt": ticket.resolved_at,
                    "createdAt": ticket.created_at,
                    "updatedAt": ticket.updated_at,
                    "requester": {
                        "id": requester.id,
                        "displayName": requester.display_name,
                        "email": requester.email,
                    }
                    if requester
                    else None,
                    "assignee": {
                        "id": assignee.id,
                        "displayName": assignee.display_name,
                        "email": assignee.email,
                    }
                    if assignee
                    else None,
                }
            )
        return output

    async def find_one(self, ticket_id: str) -> dict:
        ticket = await self.db.get(ITTicket, ticket_id)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

        requester = await self.db.get(User, ticket.requester_id)
        assignee = await self.db.get(User, ticket.assignee_id) if ticket.assignee_id else None

        comments_result = await self.db.execute(
            select(TicketComment).where(TicketComment.ticket_id == ticket_id).order_by(desc(TicketComment.created_at))
        )
        comments = []
        for comment in comments_result.scalars().all():
            user = await self.db.get(User, comment.user_id)
            comments.append(
                {
                    "id": comment.id,
                    "content": comment.content,
                    "ticketId": comment.ticket_id,
                    "userId": comment.user_id,
                    "createdAt": comment.created_at,
                    "user": {
                        "id": user.id,
                        "displayName": user.display_name,
                        "firstName": user.first_name,
                        "lastName": user.last_name,
                        "avatar": user.avatar,
                    }
                    if user
                    else None,
                }
            )

        return {
            "id": ticket.id,
            "ticketNo": ticket.ticket_no,
            "title": ticket.title,
            "description": ticket.description,
            "category": ticket.category,
            "priority": ticket.priority,
            "location": ticket.location,
            "status": ticket.status,
            "requesterId": ticket.requester_id,
            "assigneeId": ticket.assignee_id,
            "isAssetRequest": ticket.is_asset_request,
            "assetId": ticket.asset_id,
            "quantity": ticket.quantity,
            "expectedDate": ticket.expected_date,
            "approverId": ticket.approver_id,
            "issuedAt": ticket.issued_at,
            "issuedBy": ticket.issued_by,
            "resolvedAt": ticket.resolved_at,
            "createdAt": ticket.created_at,
            "updatedAt": ticket.updated_at,
            "requester": {
                "id": requester.id,
                "displayName": requester.display_name,
            }
            if requester
            else None,
            "assignee": {
                "id": assignee.id,
                "displayName": assignee.display_name,
            }
            if assignee
            else None,
            "comments": comments,
        }

    async def update(self, ticket_id: str, payload: UpdateITTicketDto) -> dict:
        ticket = await self.db.get(ITTicket, ticket_id)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

        current_status = ticket.status
        data = payload.model_dump(exclude_unset=True)

        mapping = {
            "assigneeId": "assignee_id",
            "assetId": "asset_id",
            "expectedDate": "expected_date",
            "approverId": "approver_id",
            "isAssetRequest": "is_asset_request",
            "issuedBy": "issued_by",
            "createdAt": "created_at",
            "resolvedAt": "resolved_at",
        }

        for key, value in data.items():
            target = mapping.get(key, key)
            if target in {"created_at", "resolved_at", "expected_date"} and value:
                value = self._parse_datetime(value)
            if hasattr(ticket, target):
                setattr(ticket, target, value)

        if data.get("status") in ["Resolved", "Closed"] and current_status not in ["Resolved", "Closed"]:
            if not data.get("resolvedAt"):
                ticket.resolved_at = datetime.now()

        await self.db.commit()

        if ticket.is_asset_request and data.get("status") == "Approved" and current_status != "Approved":
            if ticket.asset_id and ticket.quantity and ticket.quantity > 0:
                try:
                    asset = await self.db.get(ITAsset, ticket.asset_id)
                    if asset:
                        asset.stock = max(0, asset.stock - ticket.quantity)
                        await self.db.commit()
                except Exception:
                    pass

        if data.get("status"):
            await self._trigger_notification(
                "IT_HELP_DESK",
                "TICKET_UPDATED",
                {
                    "title": f"Ticket Updated: {ticket.ticket_no}",
                    "message": f"Status changed to {ticket.status}",
                    "actionUrl": f"/admin/helpdesk?ticketId={ticket.id}",
                },
                explicit_user_ids=[ticket.requester_id],
            )

            if data.get("status") == "Approved":
                await self._trigger_notification(
                    "IT_HELP_DESK",
                    "ASSET_APPROVED",
                    {
                        "title": f"Asset Request Approved: {ticket.ticket_no}",
                        "message": "Approved by Approver. Ready for processing.",
                        "actionUrl": f"/admin/helpdesk?ticketId={ticket.id}",
                    },
                )

        if data.get("assigneeId"):
            await self._trigger_notification(
                "IT_HELP_DESK",
                "TICKET_ASSIGNED",
                {
                    "title": f"Ticket Assigned: {ticket.ticket_no}",
                    "message": f"You have been assigned to ticket {ticket.ticket_no}",
                    "actionUrl": f"/admin/helpdesk?ticketId={ticket.id}",
                },
                explicit_user_ids=[data["assigneeId"]],
            )

        return await self.find_one(ticket_id)

    async def remove(self, ticket_id: str) -> dict:
        ticket = await self.db.get(ITTicket, ticket_id)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
        data = {"id": ticket.id, "ticketNo": ticket.ticket_no}
        await self.db.delete(ticket)
        await self.db.commit()
        return data

    async def add_comment(self, ticket_id: str, user_id: str, payload: CreateTicketCommentDto) -> dict:
        ticket = await self.db.get(ITTicket, ticket_id)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

        comment = TicketComment(
            id=str(uuid4()),
            content=payload.content,
            ticket_id=ticket_id,
            user_id=user_id,
        )
        self.db.add(comment)
        await self.db.commit()
        await self.db.refresh(comment)

        user = await self.db.get(User, user_id)
        targets = []
        if user_id != ticket.requester_id:
            targets.append(ticket.requester_id)
        if ticket.assignee_id and user_id != ticket.assignee_id:
            targets.append(ticket.assignee_id)

        if targets:
            await self._trigger_notification(
                "IT_HELP_DESK",
                "NEW_COMMENT",
                {
                    "title": f"New Comment on {ticket.ticket_no}",
                    "message": f"{user.display_name if user else 'Someone'} commented on the ticket",
                    "actionUrl": f"/admin/helpdesk?ticketId={ticket.id}",
                },
                explicit_user_ids=targets,
            )

        return {
            "id": comment.id,
            "content": comment.content,
            "ticketId": comment.ticket_id,
            "userId": comment.user_id,
            "createdAt": comment.created_at,
            "user": {
                "id": user.id,
                "displayName": user.display_name,
                "firstName": user.first_name,
                "lastName": user.last_name,
                "avatar": user.avatar,
            }
            if user
            else None,
        }

    async def _trigger_notification(
        self,
        source_app: str,
        action_type: str,
        payload: dict,
        explicit_user_ids: list[str] | None = None,
        notification_type: str = "INFO",
    ) -> None:
        try:
            target_user_ids = list(explicit_user_ids or [])

            result = await self.db.execute(
                select(NotificationSetting).where(
                    NotificationSetting.source_app == source_app, NotificationSetting.action_type == action_type
                )
            )
            setting = result.scalar_one_or_none()

            if setting and setting.is_active:
                roles = list(setting.recipient_roles or [])
                groups = list(setting.recipient_groups or [])

                if roles:
                    role_result = await self.db.execute(select(Role).where(Role.name.in_(roles)))
                    role_ids = [row.id for row in role_result.scalars().all()]
                    user_result = await self.db.execute(
                        select(User).where(or_(User.role.in_(roles), User.role_id.in_(role_ids)))
                    )
                    target_user_ids.extend([item.id for item in user_result.scalars().all()])

                if groups:
                    group_result = await self.db.execute(select(NotificationGroup).where(NotificationGroup.id.in_(groups)))
                    for group in group_result.scalars().all():
                        await self.db.refresh(group, ["members"])
                        target_user_ids.extend([member.id for member in group.members])

            unique_ids = list(set(target_user_ids))
            for uid in unique_ids:
                await self.notifications.create(
                    {
                        "userId": uid,
                        "title": payload.get("title"),
                        "message": payload.get("message"),
                        "type": notification_type,
                        "sourceApp": source_app,
                        "actionType": action_type,
                        "actionUrl": payload.get("actionUrl"),
                    }
                )
        except Exception:
            pass
