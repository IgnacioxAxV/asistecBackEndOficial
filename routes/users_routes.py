from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
import schemas
from database import get_db
from controllers.users_controllers import get_all_users, get_user_by_id, get_user_next_activities, activate_user, update_profile_image
from interfaces.auth_factory import AuthFactory

user_router = APIRouter(prefix="/api/users", tags=["Users"])

@user_router.get("/", response_model=list[schemas.UserListResponse])
def get_all_users_route(db: Session = Depends(get_db)):
    return get_all_users(db)

@user_router.get("/next_activities", response_model=list)
def get_user_next_activities_route(user_id: str, db: Session = Depends(get_db)):
    return get_user_next_activities(user_id, db)

@user_router.get("/{user_id}", response_model=schemas.UserListResponse)
def get_user_by_id_route(user_id: str, db: Session = Depends(get_db)):
    return get_user_by_id(user_id, db)

@user_router.post("/user_create", status_code=status.HTTP_201_CREATED)
def create_user_route(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        provider = AuthFactory.get_auth_provider(user.mail)
    except ValueError:
        raise HTTPException(status_code=400, detail="Dominio de correo no permitido")

    return provider.create_user(user, db)

@user_router.post("/user_login")
def login_user_route(user: schemas.UserLogin, db: Session = Depends(get_db)):
    try:
        provider = AuthFactory.get_auth_provider(user.mail)
    except ValueError:
        raise HTTPException(status_code=400, detail="Dominio de correo no permitido")

    return provider.login(user, db)

@user_router.put("/activate", response_model=dict)
def activate_user_route(user_id: str, db: Session = Depends(get_db)):
    return activate_user(user_id, db)

@user_router.put("/profile_image", response_model=dict)
def update_profile_image_route(user_id: str, data: schemas.ProfileImageUpdate, db: Session = Depends(get_db)):
    return update_profile_image(user_id, data.profile_image, db)
