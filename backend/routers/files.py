import os
import aiofiles
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from ..auth import get_current_user

router = APIRouter(tags=["files"])

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _assert_member(db, room_id, user_id):
    m = db.query(models.RoomMember).filter(
        models.RoomMember.room_id == room_id,
        models.RoomMember.user_id == user_id,
    ).first()
    if not m:
        raise HTTPException(status_code=403, detail="Not a member of this room")


@router.post("/api/rooms/{room_id}/files", response_model=schemas.FileOut)
async def upload_file(
    room_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _assert_member(db, room_id, current_user.id)

    safe_name = f"{room_id}_{current_user.id}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, safe_name)

    async with aiofiles.open(filepath, "wb") as f:
        content = await file.read()
        await f.write(content)

    db_file = models.File(
        room_id=room_id,
        uploaded_by=current_user.id,
        filename=file.filename,
        filepath=safe_name,
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file


@router.get("/api/rooms/{room_id}/files", response_model=list[schemas.FileOut])
def list_files(room_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    _assert_member(db, room_id, current_user.id)
    return db.query(models.File).filter(models.File.room_id == room_id).all()


@router.get("/api/files/{file_id}/download")
def download_file(file_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_file = db.query(models.File).filter(models.File.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    _assert_member(db, db_file.room_id, current_user.id)

    full_path = os.path.join(UPLOAD_DIR, db_file.filepath)
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="File missing on disk")
    return FileResponse(full_path, filename=db_file.filename)
