from hashlib import sha256

from aiohttp.web import HTTPForbidden
from aiohttp_apispec import docs, request_schema, response_schema
from aiohttp_session import new_session

from app.admin.schemes import AdminCreateSchema, AdminSchema
from app.web.app import View, app
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class AdminLoginView(View):
    @docs(
        tags=['admin'],
        summary='admin login',
        description='Create admin session authorization by email and password',
    )
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
    @docs(
        tags=['admin'],
        summary='create admin from config',
        description='Create admin from config',
    )
    @response_schema(AdminCreateSchema, 200)
    async def post(self):
        await self.store.admins.create_admin_after_start_app(app)
        return json_response(data={'status': 'admin successfull create'})


class AdminCurrentView(AuthRequiredMixin, View):
    @docs(
        tags=['admin'],
        summary='current admin',
        description='Shows current admin information',
    )
    @response_schema(AdminSchema, 200)
    async def get(self):
        return json_response(AdminSchema().dump(self.request.admin))
