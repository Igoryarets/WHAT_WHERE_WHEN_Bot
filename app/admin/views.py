from hashlib import sha256

from aiohttp.web import HTTPForbidden
from aiohttp_apispec import request_schema, response_schema
from aiohttp_session import new_session

from app.admin.schemes import AdminSchema
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class AdminLoginView(View):
    @request_schema(AdminSchema)
    @response_schema(AdminSchema, 200)
    async def post(self):
        # data = await self.request.json()

        email = self.data['email']
        admin = await self.store.admins.get_by_email(email)
        if not admin:
            raise HTTPForbidden
        password = self.data['password']
        if admin.password == sha256(password.encode()).hexdigest:
            raise HTTPForbidden

        # admin = await self.store.admins.create_admin(email, password)

        admin_without_password = AdminSchema().dump(admin)
        session = await new_session(self.request)
        session['admin'] = admin_without_password

        return json_response(data=admin_without_password)


class AdminCurrentView(AuthRequiredMixin, View):
    @response_schema(AdminSchema, 200)
    async def get(self):
        return json_response(AdminSchema().dump(self.request.admin))
