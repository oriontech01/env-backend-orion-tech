from fastapi import APIRouter, Depends, status, HTTPException
from .. import schemas, database, oauth2, models
from ..repositories import s3Bucket
from sqlalchemy.orm import Session
from ..repositories import admin
from typing import List




router= APIRouter(prefix="/home-models", tags= ["Home"])
get_db= database.get_database



@router.get('/get-all-models', response_model= list[schemas.HomeModelObjects], status_code= status.HTTP_200_OK)
async def get_all_models(db: Session= Depends(get_db), current_user: schemas.SignUp= Depends(oauth2.get_current_user)):
    get_user= db.query(models.Users).filter(models.Users.username== current_user.username.lower())

    if not get_user.first():
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to perform this operation")
    
    return db.query(models.ModelObject).all()

    # object_to_json_list= []
    # for i in db_query:
    #     bucket_folder_path= f'teacher/courses/{i.id}/cover_picture'

    #     # object_to_json= schemas.CoursesTags.parse_obj(i)#TP MAKE THIS WORK, YOU WIL HAVE TO SET THE from orm TO TRUE IN THE SCHEMA MODEL CLASS CONFIG, SO THIS WILL THEN BE ABLE TO PARSE IN THE OBJECT
    #     picture_get_preferred_link= await s3Bucket.s3_get_presigned_link(i.picture_cover)

    #     file_get_preferred_link= await s3Bucket.s3_get_presigned_link(i.file_model)

    #     object_to_json= schemas.HomeModelObjects(
    #         date_and_time_of_sample= i.date_and_time_of_sample,
    #         id= i.id,
    #         description_model= i.description_model,
    #         file_model= file_get_preferred_link,
    #         picture_cover= picture_get_preferred_link,
    #         objects_relationship= i.objects_relationship,
    #     )

    #     object_to_json_list.append(object_to_json)

    # return object_to_json_list






@router.get('/get-a-model/{model_id}', response_model= schemas.HomeModelObjects, status_code= status.HTTP_200_OK)
async def get_a_models(model_id: str, db: Session= Depends(get_db), current_user: schemas.SignUp= Depends(oauth2.get_current_user)):

    get_user= db.query(models.Users).filter(models.Users.username== current_user.username.lower())

    if not get_user.first():
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to perform this operation")

    get_model_object= db.query(models.ModelObject).filter(models.ModelObject.id == model_id)

    if not get_model_object.first():
                raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="Model with this id does not exist or has been deleted")
    return get_model_object.first();


    # # object_to_json= schemas.CoursesTags.parse_obj(i)#TP MAKE THIS WORK, YOU WIL HAVE TO SET THE from orm TO TRUE IN THE SCHEMA MODEL CLASS CONFIG, SO THIS WILL THEN BE ABLE TO PARSE IN THE OBJECT
    # picture_get_preferred_link= await s3Bucket.s3_get_presigned_link(db_query.picture_cover)

    # file_get_preferred_link= await s3Bucket.s3_get_presigned_link(db_query.file_model)

    # object_to_json= schemas.HomeModelObjects(
    #     date_and_time_of_sample= db_query.date_and_time_of_sample,
    #     id= db_query.id,
    #     description_model= db_query.description_model,
    #     file_model= file_get_preferred_link,
    #     picture_cover= picture_get_preferred_link,
    #     objects_relationship= db_query.objects_relationship,
    # )


    # return object_to_json


