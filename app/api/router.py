from fastapi import APIRouter, HTTPException

from app.api.routes.approvals import router as approvals_router
from app.api.routes.auth import router as auth_router
from app.api.routes.bookings import router as bookings_router
from app.api.routes.cpk_analyses import router as cpk_analyses_router
from app.api.routes.e_signatures import router as e_signatures_router
from app.api.routes.health import router as health_router
from app.api.routes.it_assets import router as it_assets_router
from app.api.routes.it_tickets import router as it_tickets_router
from app.api.routes.job_orders import router as job_orders_router
from app.api.routes.knowledge_books import router as knowledge_books_router
from app.api.routes.maintenance import router as maintenance_router
from app.api.routes.master import router as master_router
from app.api.routes.mymachine import router as mymachine_router
from app.api.routes.notification_groups import router as notification_groups_router
from app.api.routes.access_control import router as access_control_router
from app.api.routes.analytics import router as analytics_router
from app.api.routes.plc import router as plc_router
from app.api.routes.printer_usage import router as printer_usage_router
from app.api.routes.notifications import router as notifications_router
from app.api.routes.pools import router as pools_router
from app.api.routes.posts import router as posts_router
from app.api.routes.production_reports import router as production_reports_router
from app.api.routes.raw_material_plans import router as raw_material_plans_router
from app.api.routes.rubber_types import router as rubber_types_router
from app.api.routes.roles import router as roles_router
from app.api.routes.shipping_plans import router as shipping_plans_router
from app.api.routes.suppliers import router as suppliers_router
from app.api.routes.users import router as users_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(posts_router)
api_router.include_router(roles_router)
api_router.include_router(notification_groups_router)
api_router.include_router(notifications_router)
api_router.include_router(suppliers_router)
api_router.include_router(rubber_types_router)
api_router.include_router(approvals_router)
api_router.include_router(bookings_router)
api_router.include_router(pools_router)
api_router.include_router(raw_material_plans_router)
api_router.include_router(production_reports_router)
api_router.include_router(shipping_plans_router)
api_router.include_router(cpk_analyses_router)
api_router.include_router(e_signatures_router)
api_router.include_router(it_assets_router)
api_router.include_router(it_tickets_router)
api_router.include_router(job_orders_router)
api_router.include_router(knowledge_books_router)
api_router.include_router(maintenance_router)
api_router.include_router(master_router)
api_router.include_router(mymachine_router)
api_router.include_router(access_control_router)
api_router.include_router(analytics_router)
api_router.include_router(plc_router)
api_router.include_router(printer_usage_router)

# All modules have been migrated!
