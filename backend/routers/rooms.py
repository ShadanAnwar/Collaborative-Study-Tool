import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from ..auth import get_current_user

router = APIRouter(prefix="/api/rooms", tags=["rooms"])


@router.get("", response_model=list[schemas.RoomOut])
def list_rooms(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    memberships = db.query(models.RoomMember).filter(models.RoomMember.user_id == current_user.id).all()
    room_ids = [m.room_id for m in memberships]
    return db.query(models.Room).filter(models.Room.id.in_(room_ids)).all()


@router.post("", response_model=schemas.RoomOut)
def create_room(data: schemas.RoomCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    room = models.Room(
        name=data.name,
        description=data.description,
        owner_id=current_user.id,
        invite_code=str(uuid.uuid4())[:8].upper(),
    )
    db.add(room)
    db.commit()
    db.refresh(room)

    # Owner auto-joins as admin
    member = models.RoomMember(room_id=room.id, user_id=current_user.id, role="admin")
    db.add(member)
    db.commit()
    return room


@router.post("/{room_id}/join", response_model=schemas.RoomOut)
def join_room(room_id: int, data: schemas.RoomJoin, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if room.invite_code != data.invite_code:
        raise HTTPException(status_code=403, detail="Invalid invite code")

    existing = db.query(models.RoomMember).filter(
        models.RoomMember.room_id == room_id,
        models.RoomMember.user_id == current_user.id,
    ).first()
    if existing:
        return room

    member = models.RoomMember(room_id=room_id, user_id=current_user.id, role="member")
    db.add(member)
    db.commit()
    return room


@router.post("/join-by-code", response_model=schemas.RoomOut)
def join_room_by_code(data: schemas.RoomJoin, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    room = db.query(models.Room).filter(models.Room.invite_code == data.invite_code).first()
    if not room:
        raise HTTPException(status_code=404, detail="Invalid invite code")

    existing = db.query(models.RoomMember).filter(
        models.RoomMember.room_id == room.id,
        models.RoomMember.user_id == current_user.id,
    ).first()
    if not existing:
        member = models.RoomMember(room_id=room.id, user_id=current_user.id, role="member")
        db.add(member)
        db.commit()
    return room


@router.get("/{room_id}/members", response_model=list[schemas.MemberOut])
def get_members(room_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    _assert_member(db, room_id, current_user.id)
    return db.query(models.RoomMember).filter(models.RoomMember.room_id == room_id).all()


@router.get("/{room_id}", response_model=schemas.RoomOut)
def get_room(room_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    _assert_member(db, room_id, current_user.id)
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


def _assert_member(db, room_id, user_id):
    m = db.query(models.RoomMember).filter(
        models.RoomMember.room_id == room_id,
        models.RoomMember.user_id == user_id,
    ).first()
    if not m:
        raise HTTPException(status_code=403, detail="Not a member of this room")
