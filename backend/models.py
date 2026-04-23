from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base


class RoleEnum(str, enum.Enum):
    admin = "admin"
    member = "member"


class StatusEnum(str, enum.Enum):
    todo = "todo"
    inprogress = "inprogress"
    done = "done"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    owned_rooms = relationship("Room", back_populates="owner")
    memberships = relationship("RoomMember", back_populates="user")
    tasks_assigned = relationship("Task", foreign_keys="Task.assigned_to", back_populates="assignee")
    tasks_created = relationship("Task", foreign_keys="Task.created_by", back_populates="creator")
    messages = relationship("Message", back_populates="user")
    files = relationship("File", back_populates="uploader")


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    owner_id = Column(Integer, ForeignKey("users.id"))
    invite_code = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="owned_rooms")
    members = relationship("RoomMember", back_populates="room")
    tasks = relationship("Task", back_populates="room")
    messages = relationship("Message", back_populates="room")
    files = relationship("File", back_populates="room")


class RoomMember(Base):
    __tablename__ = "room_members"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(Enum(RoleEnum), default=RoleEnum.member)

    room = relationship("Room", back_populates="members")
    user = relationship("User", back_populates="memberships")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    title = Column(String, nullable=False)
    status = Column(Enum(StatusEnum), default=StatusEnum.todo)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    room = relationship("Room", back_populates="tasks")
    assignee = relationship("User", foreign_keys=[assigned_to], back_populates="tasks_assigned")
    creator = relationship("User", foreign_keys=[created_by], back_populates="tasks_created")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    room = relationship("Room", back_populates="messages")
    user = relationship("User", back_populates="messages")


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    room = relationship("Room", back_populates="files")
    uploader = relationship("User", back_populates="files")
