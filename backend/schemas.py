from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ── Auth ──────────────────────────────────────────────────────────────────────
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


# ── Rooms ─────────────────────────────────────────────────────────────────────
class RoomCreate(BaseModel):
    name: str
    description: Optional[str] = ""


class RoomOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    owner_id: int
    invite_code: str
    created_at: datetime

    class Config:
        from_attributes = True


class RoomJoin(BaseModel):
    invite_code: str


class MemberOut(BaseModel):
    id: int
    user_id: int
    room_id: int
    role: str
    user: UserOut

    class Config:
        from_attributes = True


# ── Tasks ─────────────────────────────────────────────────────────────────────
class TaskCreate(BaseModel):
    title: str
    assigned_to: Optional[int] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[int] = None


class TaskOut(BaseModel):
    id: int
    room_id: int
    title: str
    status: str
    assigned_to: Optional[int]
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── Files ─────────────────────────────────────────────────────────────────────
class FileOut(BaseModel):
    id: int
    room_id: int
    uploaded_by: int
    filename: str
    filepath: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── Messages ──────────────────────────────────────────────────────────────────
class MessageOut(BaseModel):
    id: int
    room_id: int
    user_id: int
    content: str
    created_at: datetime
    user: UserOut

    class Config:
        from_attributes = True
