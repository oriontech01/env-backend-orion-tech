from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, Query, File
from .. import schemas, database, oauth2, models
from sqlalchemy.orm import Session
from ..repositories import add_model_object
from . import authentication
from fastapi.security import OAuth2PasswordRequestForm
from typing import List, Union, Annotated

import os
from dotenv import load_dotenv
from ..hashing import Hash

load_dotenv()

router= APIRouter(prefix="/admin", tags= ["Models"])
get_db= database.get_database


USERNAME= os.getenv('ADMIN_USER') ,
ROLE=  os.getenv('ADMIN_ROLE') ,

# @router.post('/add-model2', status_code= status.HTTP_201_CREATED)
# async def add_model2(current_user: schemas.SignUp= Depends(oauth2.get_current_user)):
#     print(current_user.username)

# request_body: Annotated[Union[str, None], Query()]= None

@router.post('/add-model', status_code= status.HTTP_201_CREATED)
async def add_model(picture_cover: UploadFile= File, model_object: UploadFile= File, request_body: schemas.ModelObjectFormModfied= Depends(),  db: Session= Depends(get_db), current_user: schemas.SignUp= Depends(oauth2.get_current_user)):
    # request_to_json= schemas.ModelObjectFormModfied.model_validate_json(request_body)
    
    return await add_model_object.add_model(request_body, picture_cover, model_object, current_user.username, db)



@router.post('/object-add-model', status_code= status.HTTP_201_CREATED)
async def object_add_model(request_body: schemas.ObjectModelObjectForm,  db: Session= Depends(get_db), current_user: schemas.SignUp= Depends(oauth2.get_current_user)):

    return await add_model_object.object_add_model(request_body, current_user.username, db)


@router.put('/update-model-super-admin', status_code= status.HTTP_201_CREATED)
async def update_model_super_admin(picture_cover: Union[UploadFile, None]= None, request_body: Annotated[Union[str, None], Query()]= None, db: Session= Depends(get_db), current_user: schemas.SignUp= Depends(oauth2.get_current_user)):
    # print (request_body) 
    request_to_json= schemas.ModelObjectFormUpdate.model_validate_json(request_body)
    # print(request_to_json)
    return await add_model_object.update_model_super_admin(request_to_json, picture_cover, current_user.username, db)


@router.put('/update-model-admin', status_code= status.HTTP_201_CREATED)
async def update_model_admin(picture_cover: Union[UploadFile, None]= None, request_body: Annotated[Union[str, None], Query()]= None, db: Session= Depends(get_db), current_user: schemas.SignUp= Depends(oauth2.get_current_user)):
    # print (request_body) 
    request_to_json= schemas.ModelObjectFormUpdate.model_validate_json(request_body)
    # print(request_to_json)
    return await add_model_object.update_model_admin(request_to_json, picture_cover, current_user.username, db)



@router.delete('/delete-model-super-admin', status_code= status.HTTP_204_NO_CONTENT)
async def delete_model_super_admin(id: List[str], db: Session= Depends(get_db), current_user: schemas.SignUp= Depends(oauth2.get_current_user)):
    return await add_model_object.delete_model_super_admin(id, current_user.username, db)

@router.delete('/delete-object-super-admin', status_code= status.HTTP_204_NO_CONTENT)
async def delete_object_super_admin(id: List[int], db: Session= Depends(get_db), current_user: schemas.SignUp= Depends(oauth2.get_current_user)):
    return await add_model_object.delete_object_super_admin(id, current_user.username, db)



@router.delete('/delete-model-admin', status_code= status.HTTP_204_NO_CONTENT)
async def delete_model_admin(id: List[str], db: Session= Depends(get_db), current_user: schemas.SignUp= Depends(oauth2.get_current_user)):
    return await add_model_object.delete_model_admin(id, current_user.username, db)

@router.delete('/delete-object-admin', status_code= status.HTTP_204_NO_CONTENT)
async def delete_object_admin(id: List[int], db: Session= Depends(get_db), current_user: schemas.SignUp= Depends(oauth2.get_current_user)):
    return await add_model_object.delete_object_admin(id, current_user.username, db)



