import logging
from hashlib import sha256
from typing import Optional

from sqlalchemy import select

from app.admin.models import Admin, AdminModel
from app.base.base_accessor import BaseAccessor
from app.web.app import Application


class AdminAccessor(BaseAccessor):
    async def get_by_email(self, email: str) -> Optional[Admin]:
        async with self.app.database.session() as db:

            admin = await db.execute(
                select(AdminModel).where(
                    AdminModel.email == email))
            try:
                (res, ) = admin.first()
                return Admin(id=res.id, email=res.email, password=res.password)
            except TypeError:
                return None

    async def create_admin_after_start_app(self, app: Application) -> None:
        email = self.app.config.admin.email
        passward = self.app.config.admin.password
        admin = await self.get_by_email(email)
        if not admin:
            await self.create_admin(email, passward)
            logging.info('Create admin after start app')

    async def create_admin(self, email: str, password: str) -> None:
        async with self.app.database.session() as db:
            admin = AdminModel(
                email=email,
                password=sha256(password.encode()).hexdigest(),
            )
            db.add(admin)
            await db.commit()
