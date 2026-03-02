from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import db_session_dependency, get_current_user, permissions_required
from app.core.permissions import BOOKINGS_CREATE, BOOKINGS_DELETE, BOOKINGS_READ, BOOKINGS_UPDATE
from app.schemas.booking import (
    BookingSampleDto,
    BookingWeightInDto,
    BookingWeightOutDto,
    CreateBookingDto,
    GenericBodyDto,
    UpdateBookingDto,
)
from app.services.bookings_service import BookingsService

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("", dependencies=[Depends(get_current_user), Depends(permissions_required(BOOKINGS_CREATE))])
async def create_booking(payload: CreateBookingDto, db: AsyncSession = Depends(db_session_dependency)):
    return await BookingsService(db).create(payload)


@router.get("", dependencies=[Depends(get_current_user), Depends(permissions_required(BOOKINGS_READ))])
async def find_all_bookings(
    date: str | None = Query(default=None),
    slot: str | None = Query(default=None),
    code: str | None = Query(default=None),
    db: AsyncSession = Depends(db_session_dependency),
):
    return await BookingsService(db).find_all(date=date, slot=slot, code=code)


@router.get("/stats/{date}", dependencies=[Depends(get_current_user), Depends(permissions_required(BOOKINGS_READ))])
async def get_stats(date: str, db: AsyncSession = Depends(db_session_dependency)):
    return await BookingsService(db).get_stats(date)


@router.get("/{booking_id}/samples", dependencies=[Depends(get_current_user), Depends(permissions_required(BOOKINGS_READ))])
async def get_samples(booking_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await BookingsService(db).get_samples(booking_id)


@router.post("/{booking_id}/samples", dependencies=[Depends(get_current_user), Depends(permissions_required(BOOKINGS_CREATE))])
async def save_sample(
    booking_id: str,
    payload: BookingSampleDto,
    db: AsyncSession = Depends(db_session_dependency),
):
    return await BookingsService(db).save_sample(booking_id, payload)


@router.delete(
    "/{booking_id}/samples/{sample_id}",
    dependencies=[Depends(get_current_user), Depends(permissions_required(BOOKINGS_DELETE))],
)
async def delete_sample(booking_id: str, sample_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await BookingsService(db).delete_sample(booking_id, sample_id)


@router.get("/{booking_id}", dependencies=[Depends(get_current_user), Depends(permissions_required(BOOKINGS_READ))])
async def find_one_booking(booking_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await BookingsService(db).find_one(booking_id)


@router.patch("/{booking_id}", dependencies=[Depends(get_current_user), Depends(permissions_required(BOOKINGS_UPDATE))])
async def update_booking(
    booking_id: str,
    payload: UpdateBookingDto,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(db_session_dependency),
):
    return await BookingsService(db).update(booking_id, payload, current_user)


@router.patch("/{booking_id}/check-in", dependencies=[Depends(get_current_user)])
async def check_in(
    booking_id: str,
    body: GenericBodyDto,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(db_session_dependency),
):
    permissions = current_user.get("permissions") or []
    role = current_user.get("role")
    has_permission = role == "ADMIN" or any(
        item in permissions for item in ["bookings:update", "truckScale:create", "truckScale:update"]
    )
    if not has_permission:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to Check In (requires bookings:update or truckScale:create/update)",
        )
    return await BookingsService(db).check_in(booking_id, body.model_dump(exclude_unset=True), current_user)


@router.patch("/{booking_id}/start-drain", dependencies=[Depends(get_current_user), Depends(permissions_required(BOOKINGS_UPDATE))])
async def start_drain(
    booking_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(db_session_dependency),
):
    return await BookingsService(db).start_drain(booking_id, current_user)


@router.patch("/{booking_id}/stop-drain", dependencies=[Depends(get_current_user), Depends(permissions_required(BOOKINGS_UPDATE))])
async def stop_drain(
    booking_id: str,
    body: GenericBodyDto,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(db_session_dependency),
):
    return await BookingsService(db).stop_drain(booking_id, body.model_dump(exclude_unset=True), current_user)


@router.patch("/{booking_id}/weight-in", dependencies=[Depends(get_current_user), Depends(permissions_required(BOOKINGS_UPDATE))])
async def save_weight_in(
    booking_id: str,
    body: BookingWeightInDto,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(db_session_dependency),
):
    return await BookingsService(db).save_weight_in(booking_id, body.model_dump(exclude_unset=True), current_user)


@router.patch("/{booking_id}/weight-out", dependencies=[Depends(get_current_user), Depends(permissions_required(BOOKINGS_UPDATE))])
async def save_weight_out(
    booking_id: str,
    body: BookingWeightOutDto,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(db_session_dependency),
):
    return await BookingsService(db).save_weight_out(booking_id, body.model_dump(exclude_unset=True), current_user)


@router.delete("/{booking_id}", dependencies=[Depends(get_current_user), Depends(permissions_required(BOOKINGS_DELETE))])
async def remove_booking(
    booking_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(db_session_dependency),
):
    return await BookingsService(db).remove(booking_id, current_user)
