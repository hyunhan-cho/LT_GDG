# account/schemas.py
from ninja import Schema
from typing import Optional
from uuid import UUID

class CompanyCreateSchema(Schema):
    name: str
    registration_number: str
    industry: Optional[str] = None

class DepartmentCreateSchema(Schema):
    company_id: UUID 
    code: str
    name: str

class UserSignupSchema(Schema):
    username: str
    password: str
    password_confirm: str
    korean_name: str
    employee_id: str
    company_id: UUID
    department_id: Optional[int] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None

class UserLoginSchema(Schema):
    username: str
    password: str

class TokenSchema(Schema):
    access: str
    refresh: str

class UserInfoSchema(Schema):
    id: int
    username: str
    korean_name: str
    employee_id: str
    company_name: Optional[str] = None
    department_name: Optional[str] = None

class LoginResponseSchema(Schema):
    message: str
    token: TokenSchema
    user: UserInfoSchema