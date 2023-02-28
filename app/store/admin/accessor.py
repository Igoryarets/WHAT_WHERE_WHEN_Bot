from typing import Optional

from sqlalchemy import select

from app.admin.models import Admin, AdminModel
from app.base.base_accessor import BaseAccessor


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

    async def create_admin(self, email: str, password: str) -> Admin:
        admin = AdminModel(email=email, password=password)
        async with self.app.database.session() as db:
            db.add(admin)
            try:
                await db.commit()
            except Exception:
                await db.rollback(admin)
                raise
            else:
                await db.refresh(admin)
            return Admin(
                id=admin.id, email=admin.email, password=admin.password)
