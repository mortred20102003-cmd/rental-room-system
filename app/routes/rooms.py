from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.dependencies import get_current_owner
from app.controllers.room_controller import RoomController
from app.schemas.room import RoomCreate, RoomUpdate, RoomResponse

router = APIRouter(prefix="/rooms", tags=["Rooms"])

@router.get("/", response_model=List[RoomResponse])
def list_rooms(property_id: Optional[int] = None,
               occupied: Optional[bool] = None,
               skip: int = 0, limit: int = 100,
               db: Session = Depends(get_db),
               owner=Depends(get_current_owner)):
    return RoomController(db).list(property_id, occupied, skip, limit)

@router.get("/{rid}", response_model=RoomResponse)
def get_room(rid: int, db: Session = Depends(get_db), owner=Depends(get_current_owner)):
    return RoomController(db).get(rid)

@router.post("/", response_model=RoomResponse)
def create_room(data: RoomCreate, db: Session = Depends(get_db),
                owner=Depends(get_current_owner)):
    return RoomController(db).create(data)

@router.put("/{rid}", response_model=RoomResponse)
def update_room(rid: int, data: RoomUpdate, db: Session = Depends(get_db),
                owner=Depends(get_current_owner)):
    return RoomController(db).update(rid, data)

@router.patch("/{rid}/occupancy", response_model=RoomResponse)
def set_occupancy(rid: int, occupied: bool,
                  db: Session = Depends(get_db), owner=Depends(get_current_owner)):
    return RoomController(db).set_occupied(rid, occupied)

@router.delete("/{rid}")
def delete_room(rid: int, db: Session = Depends(get_db),
                owner=Depends(get_current_owner)):
    return RoomController(db).delete(rid)