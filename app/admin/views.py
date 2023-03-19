from hashlib import sha256

from aiohttp.web import HTTPForbidden
from aiohttp_apispec import request_schema, response_schema
from aiohttp_session import new_session

from app.admin.schemes import AdminSchema, AdminCreateSchema
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response
from app.web.app import app


class AdminLoginView(View):
    @request_schema(AdminSchema)
    @response_schema(AdminSchema, 200)
    async def post(self):
        email = self.data['email']
        admin = await self.store.admins.get_by_email(email)
        if not admin:
            raise HTTPForbidden
        password = self.data['password']
        if admin.password == sha256(password.encode()).hexdigest:
            raise HTTPForbidden

        admin_without_password = AdminSchema().dump(admin)
        session = await new_session(self.request)
        session['admin'] = admin_without_password

        return json_response(data=admin_without_password)


class CreateAdminView(View):
    @response_schema(AdminCreateSchema, 200)
    async def post(self):
        await self.store.admins.create_admin_after_start_app(app)
        return json_response(data={'status': 'admin successfull create'})


class AdminCurrentView(AuthRequiredMixin, View):
    @response_schema(AdminSchema, 200)
    async def get(self):
        return json_response(AdminSchema().dump(self.request.admin))
