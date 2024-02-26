from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, Query, File
from .. import schemas, database, oauth2, models
from sqlalchemy.orm import Session
from ..repositories import admin
from . import authentication
from fastapi.security import OAuth2PasswordRequestForm
from typing import List, Union, Annotated

import os
from dotenv import load_dotenv
from ..hashing import Hash

load_dotenv()

router= APIRouter(prefix="/admin", tags= ["Admins"])
get_db= database.get_database


USERNAME= os.getenv('ADMIN_USER') ,
ROLE=  os.getenv('ADMIN_ROLE') ,
try:
    PASSWORD= Hash.enc(os.getenv('ADMIN_PASSWORD'))
except:
    pass

@router.get('/auto-create-admin', status_code= status.HTTP_201_CREATED)
async def auto_create_admin( db: Session= Depends(get_db)):
    if db.query(models.Users).filter(models.Users.username== USERNAME).first():
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN)
    admin_as_user= models.Users(username= USERNAME, role= ROLE, password= PASSWORD)
    db.add(admin_as_user)
    db.commit()
    db.refresh(admin_as_user)




@router.get('/manual_verify_user',status_code= status.HTTP_200_OK)
def manual_verify(db: Session= Depends(get_db), current_user: schemas.SignUp= Depends(oauth2.get_current_user)):
    user_instance= db.query(models.Users).filter(models.Users.username == current_user.username)
    print(user_instance.first())
    print(current_user.username)
    if user_instance.first() == None:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED)
    
    return user_instance.first().role


# {
#   "username": "string",
#   "role": "string",
#   "password": "string"
# }


# request_body: Annotated[Union[str, None], Query()]= None
@router.post('/register', status_code= status.HTTP_201_CREATED)
async def admin_sign_up(picture_cover: UploadFile, request_body: schemas.SignUp= Depends(), db: Session= Depends(get_db), current_user: schemas.SignUp= Depends(oauth2.get_current_user)):
    # request_to_json= schemas.SignUp.model_validate_json(request_body)

    return await admin.admin_sign_up(picture_cover, request_body, current_user.username, db)


@router.put('/update-user-role', status_code= status.HTTP_201_CREATED)
async def admin_update_role(request: schemas.RoleUpdate, db: Session= Depends(get_db), current_user: schemas.SignUp= Depends(oauth2.get_current_user)):
    return await admin.admin_update_role(request, current_user.username, db)


@router.get('/get-all-users', response_model= list[schemas.Users], status_code= status.HTTP_200_OK)
async def get_all_users(db: Session= Depends(get_db), current_user: schemas.SignUp= Depends(oauth2.get_current_user)):
    return await admin.get_all_users(current_user.username, db)

@router.get('/get-user', response_model= schemas.Users, status_code= status.HTTP_200_OK)
async def get_user(db: Session= Depends(get_db), current_user: schemas.SignUp= Depends(oauth2.get_current_user)):
    return await admin.get_user(current_user.username, db)

@router.get('/get-user-by-username', response_model= schemas.Users,  status_code= status.HTTP_200_OK)
async def get_user_by_username(username: str, db: Session= Depends(get_db), current_user: schemas.SignUp= Depends(oauth2.get_current_user)):
    return await admin.get_user_by_username(username, current_user.username, db)

@router.put('/toggle-activation', status_code= status.HTTP_200_OK)
async def toggle_activation(db: Session= Depends(get_db), current_user: schemas.SignUp= Depends(oauth2.get_current_user)):
    return await admin.toggle_activation(db, current_user.username)


@router.delete('/delete-admin', status_code= status.HTTP_200_OK)
async def delete_admin(id: List[int], db: Session= Depends(get_db), current_user: schemas.SignUp= Depends(oauth2.get_current_user)):
    return await admin.delete_admin(id, current_user.username, db)
