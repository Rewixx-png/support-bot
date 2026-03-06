from aiogram import Router
from .user import router as user_router
from .ticket import router as ticket_router

router = Router()
router.include_router(user_router)
router.include_router(ticket_router)