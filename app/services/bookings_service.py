from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import and_, asc, desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking
from app.models.booking_lab_sample import BookingLabSample
from app.models.notification_group import NotificationGroup
from app.models.notification_setting import NotificationSetting
from app.models.role import Role
from app.models.user import User
from app.schemas.booking import (BookingSampleDto, CreateBookingDto,
                                 UpdateBookingDto)
from app.services.notifications_service import NotificationsService

SLOT_QUEUE_CONFIG: dict[str, dict[str, int | None]] = {
    "08:00-09:00": {"start": 1, "limit": 4},
    "09:00-10:00": {"start": 5, "limit": 4},
    "10:00-11:00": {"start": 9, "limit": None},
    "11:00-12:00": {"start": 13, "limit": 4},
    "13:00-14:00": {"start": 17, "limit": None},
}


def _safe_float(value: Any) -> float | None:
    if value in (None, "", "-"):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _ensure_datetime(value: datetime | str) -> datetime:
    if isinstance(value, datetime):
        return value
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _slot_config(slot: str, date_value: datetime) -> dict[str, int | None]:
    if date_value.weekday() == 5 and slot == "10:00-11:00":
        return {"start": 9, "limit": None}
    return SLOT_QUEUE_CONFIG.get(slot, {"start": 1, "limit": None})


def _gen_booking_code(date_value: datetime, queue_no: int) -> str:
    yy = str(date_value.year)[-2:]
    mm = str(date_value.month).zfill(2)
    dd = str(date_value.day).zfill(2)
    qq = str(queue_no).zfill(2)
    return f"{yy}{mm}{dd}{qq}"


class BookingsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.notifications = NotificationsService(db)

    async def create(self, payload: CreateBookingDto) -> dict:
        booking_date = _ensure_datetime(payload.date)
        slot = f"{payload.startTime}-{payload.endTime}"
        slot_config = _slot_config(slot, booking_date)

        day_start = booking_date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = booking_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        day_result = await self.db.execute(
            select(Booking).where(and_(Booking.date >= day_start, Booking.date <= day_end, Booking.deleted_at.is_(None)))
        )
        day_bookings = day_result.scalars().all()

        is_uss = bool(payload.rubberType and "USS" in payload.rubberType.upper())
        prefix = "U" if is_uss else "C"

        relevant = [
            item
            for item in day_bookings
            if bool(item.rubber_type and "USS" in item.rubber_type.upper()) == is_uss
        ]
        in_slot = [item for item in relevant if item.slot == slot]

        limit = slot_config.get("limit")
        if isinstance(limit, int) and len(in_slot) >= limit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"This time slot is full for {'USS' if is_uss else 'Cuplump'}",
            )

        if payload.truckRegister:
            duplicate = next(
                (
                    item
                    for item in day_bookings
                    if item.checkin_at is None
                    and item.supplier_id == payload.supplierId
                    and item.slot == slot
                    and item.truck_register == payload.truckRegister
                ),
                None,
            )
            if duplicate:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"This truck ({payload.truckRegister}) already has a booking for this slot.",
                )

        queue_source = relevant if is_uss else [item for item in relevant if item.slot == slot]
        used = sorted([item.queue_no for item in queue_source])
        queue_no = int(slot_config["start"] or 1)
        for value in used:
            if value == queue_no:
                queue_no += 1
            elif value > queue_no:
                break

        booking_code = prefix + _gen_booking_code(booking_date, queue_no)
        existing_codes = {item.booking_code for item in day_bookings}
        while booking_code in existing_codes:
            queue_no += 1
            booking_code = prefix + _gen_booking_code(booking_date, queue_no)

        booking = Booking(
            id=str(uuid4()),
            queue_no=queue_no,
            booking_code=booking_code,
            date=booking_date,
            start_time=payload.startTime,
            end_time=payload.endTime,
            slot=slot,
            supplier_id=payload.supplierId,
            supplier_code=payload.supplierCode,
            supplier_name=payload.supplierName,
            truck_type=payload.truckType,
            truck_register=payload.truckRegister,
            rubber_type=payload.rubberType,
            estimated_weight=_safe_float(payload.estimatedWeight),
            recorder=payload.recorder or "System",
        )
        self.db.add(booking)
        await self.db.commit()
        await self.db.refresh(booking)

        await self.notifications.trigger_system_notification(
            "Booking",
            "CREATE",
            {
                "title": "New Booking Created",
                "message": f"Booking {booking.booking_code} created for {booking.supplier_name} at {booking.slot}",
                "actionUrl": f"/bookings/{booking.booking_code}",
            },
        )

        return await self._serialize_booking(booking, include_samples=False)

    async def find_all(self, date: str | None, slot: str | None, code: str | None) -> list[dict]:
        query = select(Booking)
        if code:
            query = query.where(
                or_(Booking.booking_code == code, Booking.booking_code.like(f"CANCELLED-{code}-%"))
            )
        else:
            if date:
                target = _ensure_datetime(date)
                start = target.replace(hour=0, minute=0, second=0, microsecond=0)
                end = target.replace(hour=23, minute=59, second=59, microsecond=999999)
                query = query.where(and_(Booking.date >= start, Booking.date <= end))
            if slot:
                query = query.where(Booking.slot == slot)
            query = query.where(Booking.deleted_at.is_(None))

        result = await self.db.execute(query.order_by(asc(Booking.queue_no)))
        bookings = result.scalars().all()
        return [await self._serialize_booking(item, include_samples=True) for item in bookings]

    async def find_one(self, booking_id: str) -> dict:
        booking = await self.db.get(Booking, booking_id)
        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Booking with ID {booking_id} not found")
        return await self._serialize_booking(booking, include_samples=True)

    async def update(self, booking_id: str, payload: UpdateBookingDto, user: dict | None) -> dict:
        booking = await self.db.get(Booking, booking_id)
        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Booking with ID {booking_id} not found")

        data = payload.model_dump(exclude_unset=True)
        mapping = {
            "supplierId": "supplier_id",
            "supplierCode": "supplier_code",
            "supplierName": "supplier_name",
            "truckType": "truck_type",
            "truckRegister": "truck_register",
            "rubberType": "rubber_type",
            "estimatedWeight": "estimated_weight",
            "lotNo": "lot_no",
            "trailerLotNo": "trailer_lot_no",
            "drcEst": "drc_est",
            "drcRequested": "drc_requested",
            "drcActual": "drc_actual",
            "trailerMoisture": "trailer_moisture",
            "trailerDrcEst": "trailer_drc_est",
            "trailerDrcRequested": "trailer_drc_requested",
            "trailerDrcActual": "trailer_drc_actual",
            "weightIn": "weight_in",
            "weightOut": "weight_out",
            "trailerWeightIn": "trailer_weight_in",
            "trailerWeightOut": "trailer_weight_out",
        }

        for key, value in data.items():
            if key in {"silent"}:
                continue
            target = mapping.get(key, key)
            if target in {
                "estimated_weight",
                "moisture",
                "drc_est",
                "drc_requested",
                "drc_actual",
                "trailer_moisture",
                "trailer_drc_est",
                "trailer_drc_requested",
                "trailer_drc_actual",
                "weight_in",
                "weight_out",
                "trailer_weight_in",
                "trailer_weight_out",
            }:
                value = _safe_float(value)
            if hasattr(booking, target):
                setattr(booking, target, value)

        if data.get("status") == "APPROVED":
            booking.status = "APPROVED"
            booking.approved_by = user.get("displayName") or user.get("username") or "System" if user else "System"
            booking.approved_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(booking)

        if not bool(data.get("silent")):
            await self.notifications.trigger_system_notification(
                "Booking",
                "UPDATE",
                {
                    "title": "Booking Updated",
                    "message": f"Booking {booking.booking_code} ({booking.supplier_name}) at {booking.slot} has been updated.",
                    "actionUrl": f"/bookings?code={booking.booking_code}",
                },
            )

        return await self._serialize_booking(booking, include_samples=True)

    async def check_in(self, booking_id: str, body: dict, user: dict | None) -> dict:
        booking = await self.db.get(Booking, booking_id)
        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
        if booking.checkin_at:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This booking has already been checked in.")

        booking.checkin_at = datetime.now(timezone.utc)
        booking.checked_in_by = (user or {}).get("displayName") or (user or {}).get("username") or "System"
        booking.truck_type = body.get("truckType")
        booking.truck_register = body.get("truckRegister")
        booking.note = body.get("note")
        await self.db.commit()
        await self.db.refresh(booking)

        await self.notifications.trigger_system_notification(
            "Booking",
            "UPDATE",
            {
                "title": "Truck Checked In",
                "message": f"Truck {booking.truck_register} ({booking.booking_code}) checked in.",
                "actionUrl": f"/bookings/{booking.booking_code}",
            },
        )
        return await self._serialize_booking(booking, include_samples=False)

    async def start_drain(self, booking_id: str, user: dict | None) -> dict:
        booking = await self.db.get(Booking, booking_id)
        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
        booking.start_drain_at = datetime.now(timezone.utc)
        booking.start_drain_by = (user or {}).get("displayName") or (user or {}).get("username") or "System"
        await self.db.commit()
        await self.db.refresh(booking)
        return await self._serialize_booking(booking, include_samples=False)

    async def stop_drain(self, booking_id: str, body: dict, user: dict | None) -> dict:
        booking = await self.db.get(Booking, booking_id)
        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
        booking.stop_drain_at = datetime.now(timezone.utc)
        booking.stop_drain_by = (user or {}).get("displayName") or (user or {}).get("username") or "System"
        booking.drain_note = body.get("note")
        await self.db.commit()
        await self.db.refresh(booking)
        return await self._serialize_booking(booking, include_samples=False)

    async def save_weight_in(self, booking_id: str, body: dict, user: dict | None) -> dict:
        booking = await self.db.get(Booking, booking_id)
        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
        booking.rubber_source = body.get("rubberSource")
        booking.rubber_type = body.get("rubberType")
        booking.weight_in = _safe_float(body.get("weightIn"))
        booking.weight_in_by = (user or {}).get("displayName") or (user or {}).get("username") or "System"
        booking.trailer_rubber_source = body.get("trailerRubberSource")
        booking.trailer_rubber_type = body.get("trailerRubberType")
        booking.trailer_weight_in = _safe_float(body.get("trailerWeightIn"))
        await self.db.commit()
        await self.db.refresh(booking)
        return await self._serialize_booking(booking, include_samples=False)

    async def save_weight_out(self, booking_id: str, body: dict, user: dict | None) -> dict:
        booking = await self.db.get(Booking, booking_id)
        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
        booking.weight_out = _safe_float(body.get("weightOut"))
        booking.weight_out_by = (user or {}).get("displayName") or (user or {}).get("username") or "System"
        await self.db.commit()
        await self.db.refresh(booking)
        return await self._serialize_booking(booking, include_samples=False)

    async def remove(self, booking_id: str, user: dict | None) -> dict:
        booking = await self.db.get(Booking, booking_id)
        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

        original_code = booking.booking_code
        booking.deleted_at = datetime.now(timezone.utc)
        booking.deleted_by = (user or {}).get("displayName") or (user or {}).get("username") or "System"
        booking.status = "CANCELLED"
        booking.booking_code = f"CANCELLED-{original_code}-{int(datetime.now(timezone.utc).timestamp() * 1000)}"
        await self.db.commit()
        await self.db.refresh(booking)

        await self.notifications.trigger_system_notification(
            "Booking",
            "DELETE",
            {
                "title": "Booking Cancelled",
                "message": f"Booking {original_code} ({booking.supplier_name}) at {booking.slot} has been cancelled.",
                "actionUrl": f"/bookings/{original_code}",
            },
        )
        return await self._serialize_booking(booking, include_samples=False)

    async def get_stats(self, date: str) -> dict:
        bookings = await self.find_all(date=date, slot=None, code=None)
        total = len(bookings)
        checked_in = len([item for item in bookings if item.get("checkinAt")])
        pending = total - checked_in
        slots: dict[str, Any] = {}
        for name in SLOT_QUEUE_CONFIG.keys():
            slot_items = [item for item in bookings if item.get("slot") == name]
            slots[name] = {
                "count": len(slot_items),
                "checkedIn": len([item for item in slot_items if item.get("checkinAt")]),
                "bookings": slot_items,
            }
        return {"total": total, "checkedIn": checked_in, "pending": pending, "slots": slots}

    async def get_samples(self, booking_id: str) -> list[dict]:
        result = await self.db.execute(
            select(BookingLabSample)
            .where(BookingLabSample.booking_id == booking_id)
            .order_by(asc(BookingLabSample.sample_no))
        )
        return [self._serialize_sample(item) for item in result.scalars().all()]

    async def save_sample(self, booking_id: str, payload: BookingSampleDto) -> dict:
        data = payload.model_dump(exclude_unset=True)

        if data.get("id"):
            result = await self.db.execute(select(BookingLabSample).where(BookingLabSample.id == data["id"]).limit(1))
            existing = result.scalar_one_or_none()
            if existing:
                self._apply_sample_data(existing, data)
                await self.db.commit()
                await self.db.refresh(existing)
                await self._update_booking_lab_stats(booking_id)
                return self._serialize_sample(existing)

        is_trailer = str(data.get("isTrailer", "false")).lower() == "true"
        if isinstance(data.get("isTrailer"), bool):
            is_trailer = bool(data.get("isTrailer"))

        sample_no = data.get("sampleNo")
        if not sample_no:
            latest_result = await self.db.execute(
                select(BookingLabSample)
                .where(
                    and_(
                        BookingLabSample.booking_id == booking_id,
                        BookingLabSample.is_trailer == is_trailer,
                    )
                )
                .order_by(desc(BookingLabSample.sample_no))
                .limit(1)
            )
            latest = latest_result.scalar_one_or_none()
            sample_no = (latest.sample_no if latest else 0) + 1

        sample = BookingLabSample(
            id=str(uuid4()),
            booking_id=booking_id,
            sample_no=int(sample_no),
            is_trailer=is_trailer,
        )
        self._apply_sample_data(sample, data)
        self.db.add(sample)
        await self.db.commit()
        await self.db.refresh(sample)
        await self._update_booking_lab_stats(booking_id)
        return self._serialize_sample(sample)

    async def delete_sample(self, booking_id: str, sample_id: str) -> dict:
        sample = await self.db.get(BookingLabSample, sample_id)
        if not sample:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sample not found")
        data = self._serialize_sample(sample)
        await self.db.delete(sample)
        await self.db.commit()
        await self._update_booking_lab_stats(booking_id)
        return data

    async def _update_booking_lab_stats(self, booking_id: str) -> None:
        result = await self.db.execute(select(BookingLabSample).where(BookingLabSample.booking_id == booking_id))
        samples = result.scalars().all()

        main = [item for item in samples if not item.is_trailer]
        trailer = [item for item in samples if item.is_trailer]

        booking = await self.db.get(Booking, booking_id)
        if not booking:
            return

        def avg(values: list[float]) -> float | None:
            if not values:
                return None
            return sum(values) / len(values)

        main_cp = [item.percent_cp for item in main if item.percent_cp and item.percent_cp > 0]
        trailer_cp = [item.percent_cp for item in trailer if item.percent_cp and item.percent_cp > 0]

        if main_cp:
            cp = avg(main_cp)
            booking.drc_est = cp
            booking.cp_avg = cp
        if trailer_cp:
            cp = avg(trailer_cp)
            booking.trailer_drc_est = cp
            booking.trailer_cp_avg = cp

        await self.db.commit()

    def _apply_sample_data(self, sample: BookingLabSample, data: dict) -> None:
        mapping = {
            "beforePress": "before_press",
            "basketWeight": "basket_weight",
            "cuplumpWeight": "cuplump_weight",
            "afterPress": "after_press",
            "percentCp": "percent_cp",
            "beforeBaking1": "before_baking_1",
            "afterDryerB1": "after_dryer_b1",
            "beforeLabDryerB1": "before_lab_dryer_b1",
            "afterLabDryerB1": "after_lab_dryer_b1",
            "drcB1": "drc_b1",
            "moisturePercentB1": "moisture_percent_b1",
            "drcDryB1": "drc_dry_b1",
            "labDrcB1": "lab_drc_b1",
            "recalDrcB1": "recal_drc_b1",
            "beforeBaking2": "before_baking_2",
            "afterDryerB2": "after_dryer_b2",
            "beforeLabDryerB2": "before_lab_dryer_b2",
            "afterLabDryerB2": "after_lab_dryer_b2",
            "drcB2": "drc_b2",
            "moisturePercentB2": "moisture_percent_b2",
            "drcDryB2": "drc_dry_b2",
            "labDrcB2": "lab_drc_b2",
            "recalDrcB2": "recal_drc_b2",
            "beforeBaking3": "before_baking_3",
            "afterDryerB3": "after_dryer_b3",
            "beforeLabDryerB3": "before_lab_dryer_b3",
            "afterLabDryerB3": "after_lab_dryer_b3",
            "drcB3": "drc_b3",
            "moisturePercentB3": "moisture_percent_b3",
            "drcDryB3": "drc_dry_b3",
            "labDrcB3": "lab_drc_b3",
            "recalDrcB3": "recal_drc_b3",
            "moistureFactor": "moisture_factor",
            "recalDrc": "recal_drc",
            "recordedBy": "recorded_by",
        }
        for source_key, value in data.items():
            if source_key in {"id", "sampleNo", "isTrailer"}:
                continue
            target = mapping.get(source_key, source_key)
            if hasattr(sample, target):
                if target in {
                    "before_press",
                    "basket_weight",
                    "cuplump_weight",
                    "after_press",
                    "percent_cp",
                    "before_baking_1",
                    "after_dryer_b1",
                    "before_lab_dryer_b1",
                    "after_lab_dryer_b1",
                    "drc_b1",
                    "moisture_percent_b1",
                    "drc_dry_b1",
                    "lab_drc_b1",
                    "recal_drc_b1",
                    "before_baking_2",
                    "after_dryer_b2",
                    "before_lab_dryer_b2",
                    "after_lab_dryer_b2",
                    "drc_b2",
                    "moisture_percent_b2",
                    "drc_dry_b2",
                    "lab_drc_b2",
                    "recal_drc_b2",
                    "before_baking_3",
                    "after_dryer_b3",
                    "before_lab_dryer_b3",
                    "after_lab_dryer_b3",
                    "drc_b3",
                    "moisture_percent_b3",
                    "drc_dry_b3",
                    "lab_drc_b3",
                    "recal_drc_b3",
                    "drc",
                    "moisture_factor",
                    "recal_drc",
                    "difference",
                    "p0",
                    "p30",
                    "pri",
                }:
                    value = _safe_float(value)
                setattr(sample, target, value)


    async def _serialize_booking(self, booking: Booking, include_samples: bool) -> dict:
        data = {
            "id": booking.id,
            "queueNo": booking.queue_no,
            "bookingCode": booking.booking_code,
            "date": booking.date,
            "startTime": booking.start_time,
            "endTime": booking.end_time,
            "slot": booking.slot,
            "supplierId": booking.supplier_id,
            "supplierCode": booking.supplier_code,
            "supplierName": booking.supplier_name,
            "truckType": booking.truck_type,
            "truckRegister": booking.truck_register,
            "rubberType": booking.rubber_type,
            "lotNo": booking.lot_no,
            "estimatedWeight": booking.estimated_weight,
            "moisture": booking.moisture,
            "drcEst": booking.drc_est,
            "drcRequested": booking.drc_requested,
            "drcActual": booking.drc_actual,
            "cpAvg": booking.cp_avg,
            "grade": booking.grade,
            "recorder": booking.recorder,
            "note": booking.note,
            "status": booking.status,
            "approvedBy": booking.approved_by,
            "approvedAt": booking.approved_at,
            "checkinAt": booking.checkin_at,
            "checkedInBy": booking.checked_in_by,
            "startDrainAt": booking.start_drain_at,
            "startDrainBy": booking.start_drain_by,
            "stopDrainAt": booking.stop_drain_at,
            "stopDrainBy": booking.stop_drain_by,
            "drainNote": booking.drain_note,
            "weightIn": booking.weight_in,
            "weightInBy": booking.weight_in_by,
            "weightOut": booking.weight_out,
            "weightOutBy": booking.weight_out_by,
            "rubberSource": booking.rubber_source,
            "trailerWeightIn": booking.trailer_weight_in,
            "trailerWeightOut": booking.trailer_weight_out,
            "trailerRubberType": booking.trailer_rubber_type,
            "trailerRubberSource": booking.trailer_rubber_source,
            "trailerLotNo": booking.trailer_lot_no,
            "trailerMoisture": booking.trailer_moisture,
            "trailerDrcEst": booking.trailer_drc_est,
            "trailerDrcRequested": booking.trailer_drc_requested,
            "trailerDrcActual": booking.trailer_drc_actual,
            "trailerCpAvg": booking.trailer_cp_avg,
            "trailerGrade": booking.trailer_grade,
            "createdAt": booking.created_at,
            "updatedAt": booking.updated_at,
            "deletedAt": booking.deleted_at,
            "deletedBy": booking.deleted_by,
        }
        if include_samples:
            result = await self.db.execute(
                select(BookingLabSample)
                .where(BookingLabSample.booking_id == booking.id)
                .order_by(asc(BookingLabSample.sample_no))
            )
            data["labSamples"] = [self._serialize_sample(item) for item in result.scalars().all()]
        return data

    def _serialize_sample(self, sample: BookingLabSample) -> dict:
        return {
            "id": sample.id,
            "bookingId": sample.booking_id,
            "sampleNo": sample.sample_no,
            "isTrailer": sample.is_trailer,
            "beforePress": sample.before_press,
            "basketWeight": sample.basket_weight,
            "cuplumpWeight": sample.cuplump_weight,
            "afterPress": sample.after_press,
            "percentCp": sample.percent_cp,
            "beforeBaking1": sample.before_baking_1,
            "afterDryerB1": sample.after_dryer_b1,
            "beforeLabDryerB1": sample.before_lab_dryer_b1,
            "afterLabDryerB1": sample.after_lab_dryer_b1,
            "drcB1": sample.drc_b1,
            "moisturePercentB1": sample.moisture_percent_b1,
            "drcDryB1": sample.drc_dry_b1,
            "labDrcB1": sample.lab_drc_b1,
            "recalDrcB1": sample.recal_drc_b1,
            "beforeBaking2": sample.before_baking_2,
            "afterDryerB2": sample.after_dryer_b2,
            "beforeLabDryerB2": sample.before_lab_dryer_b2,
            "afterLabDryerB2": sample.after_lab_dryer_b2,
            "drcB2": sample.drc_b2,
            "moisturePercentB2": sample.moisture_percent_b2,
            "drcDryB2": sample.drc_dry_b2,
            "labDrcB2": sample.lab_drc_b2,
            "recalDrcB2": sample.recal_drc_b2,
            "beforeBaking3": sample.before_baking_3,
            "afterDryerB3": sample.after_dryer_b3,
            "beforeLabDryerB3": sample.before_lab_dryer_b3,
            "afterLabDryerB3": sample.after_lab_dryer_b3,
            "drcB3": sample.drc_b3,
            "moisturePercentB3": sample.moisture_percent_b3,
            "drcDryB3": sample.drc_dry_b3,
            "labDrcB3": sample.lab_drc_b3,
            "recalDrcB3": sample.recal_drc_b3,
            "drc": sample.drc,
            "moistureFactor": sample.moisture_factor,
            "recalDrc": sample.recal_drc,
            "difference": sample.difference,
            "p0": sample.p0,
            "p30": sample.p30,
            "pri": sample.pri,
            "storage": sample.storage,
            "recordedBy": sample.recorded_by,
            "createdAt": sample.created_at,
            "updatedAt": sample.updated_at,
        }
