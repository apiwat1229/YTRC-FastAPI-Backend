from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import db_session_dependency, get_current_user
from app.schemas.it_ticket import CreateITTicketDto, CreateTicketCommentDto, UpdateITTicketDto
from app.services.it_tickets_service import ITTicketsService

router = APIRouter(prefix="/it-tickets", tags=["IT Tickets"])


@router.post("", dependencies=[Depends(get_current_user)])
async def create_ticket(
    payload: CreateITTicketDto,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(db_session_dependency),
):
    return await ITTicketsService(db).create(current_user["userId"], payload)


@router.get("", dependencies=[Depends(get_current_user)])
async def find_all_tickets(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(db_session_dependency),
):
    is_it = current_user.get("department") in ["Information Technology", "เทคโนโลยีสารสนเทศ (IT)"]
    return await ITTicketsService(db).find_all(current_user["userId"], is_it)


@router.get("/{ticket_id}", dependencies=[Depends(get_current_user)])
async def find_one_ticket(ticket_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await ITTicketsService(db).find_one(ticket_id)


@router.patch("/{ticket_id}", dependencies=[Depends(get_current_user)])
async def update_ticket(
    ticket_id: str,
    payload: UpdateITTicketDto,
    db: AsyncSession = Depends(db_session_dependency),
):
    return await ITTicketsService(db).update(ticket_id, payload)


@router.delete("/{ticket_id}", dependencies=[Depends(get_current_user)])
async def delete_ticket(ticket_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await ITTicketsService(db).remove(ticket_id)


@router.post("/{ticket_id}/comments", dependencies=[Depends(get_current_user)])
async def create_comment(
    ticket_id: str,
    payload: CreateTicketCommentDto,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(db_session_dependency),
):
    return await ITTicketsService(db).add_comment(ticket_id, current_user["userId"], payload)
