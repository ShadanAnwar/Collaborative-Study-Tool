from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from ..auth import get_current_user

router = APIRouter(tags=["tasks"])


def _assert_member(db, room_id, user_id):
    m = db.query(models.RoomMember).filter(
        models.RoomMember.room_id == room_id,
        models.RoomMember.user_id == user_id,
    ).first()
    if not m:
        raise HTTPException(status_code=403, detail="Not a member of this room")


@router.get("/api/rooms/{room_id}/tasks", response_model=list[schemas.TaskOut])
def list_tasks(room_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    _assert_member(db, room_id, current_user.id)
    return db.query(models.Task).filter(models.Task.room_id == room_id).all()


@router.post("/api/rooms/{room_id}/tasks", response_model=schemas.TaskOut)
def create_task(room_id: int, data: schemas.TaskCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    _assert_member(db, room_id, current_user.id)
    task = models.Task(
        room_id=room_id,
        title=data.title,
        assigned_to=data.assigned_to,
        created_by=current_user.id,
        status="todo",
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.patch("/api/tasks/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, data: schemas.TaskUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    _assert_member(db, task.room_id, current_user.id)

    if data.title is not None:
        task.title = data.title
    if data.status is not None:
        task.status = data.status
    if data.assigned_to is not None:
        task.assigned_to = data.assigned_to

    db.commit()
    db.refresh(task)
    return task


@router.delete("/api/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    _assert_member(db, task.room_id, current_user.id)
    db.delete(task)
    db.commit()
    return {"detail": "deleted"}
