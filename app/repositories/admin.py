from .. import models, schemas
from ..repositories import s3Bucket
from ..hashing import Hash
# from ..routers import otp_management
from fastapi import HTTPException, status, Response
import os
from dotenv import load_dotenv

load_dotenv()


async def admin_sign_up(picture_cover, request, username, db):
    get_admin_id= db.query(models.Users).filter(models.Users.username==username.lower())

    role= "reviewer"
    if request.role == "Reviewer":
        role= "user"
    
    if request.role == "Tagger":
        role= "admin"


    if not get_admin_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"This acoount does not exist or has been deactivated")
    
    if get_admin_id.first().role == "admin" or get_admin_id.first().role == "user":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to perform this operation")

    if request.username == os.getenv('ADMIN_USER'):
        raise HTTPException(status_code= status.HTTP_409_CONFLICT, detail="this username is already taken")
    if db.query(models.Users).filter(models.Users.username==request.username.lower()).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="this username is already taken")
    

    upload_picture_cover= await s3Bucket.s3_upload_profile_picture(picture_cover, request.username.lower())
    
    new_user= models.Users(username=request.username.lower(),
                          role= role,
                          password= Hash.enc(request.password),
                          profile_picture= upload_picture_cover
                          )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user





async def admin_update_role(request, username, db):
    get_admin_id= db.query(models.Users).filter(models.Users.username==username.lower())
    get_user_id= db.query(models.Users).filter(models.Users.id==request.id)

    if get_user_id.first().role == "superuser":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= f"Super Admin role can not be changed")

    if get_admin_id.first().role == "admin" or get_admin_id.first().role == "user":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to perform this operation")

    if not get_user_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"This account has been removed")
    
    if get_admin_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")


    role_update= {
        "role": request.role
    }
    get_user_id.update(role_update)
    db.commit()
    



async def get_all_users(username, db):
    get_admin_id= db.query(models.Users).filter(models.Users.username==username.lower())

    get_all_admins= db.query(models.Users).filter(models.Users.role != "superuser").all()

    if not get_admin_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Your account does not exist or has been removed")
    
    if get_admin_id.first().role == "admin" or get_admin_id.first().role == "user":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to view this content")
    
    if get_admin_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if not get_admin_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this username: '{username.lower()}' does not exist or has been removed")

    
    
    return get_all_admins;
    # object_to_json_list= []
    # for i in get_all_admins:
    #     bucket_folder_path= f'teacher/courses/{i.id}/cover_picture'

    #     # object_to_json= schemas.CoursesTags.parse_obj(i)#TP MAKE THIS WORK, YOU WIL HAVE TO SET THE from orm TO TRUE IN THE SCHEMA MODEL CLASS CONFIG, SO THIS WILL THEN BE ABLE TO PARSE IN THE OBJECT
    #     object_to_json= schemas.Users(
    #         id= i.id,
    #         activated= i.activated,
    #         registration_date= i.registration_date,
    #         username= i.username,
    #         role= i.role,
    #         user_models= i.user_models,
    #     )

    #     for i2 in object_to_json.user_models:
    #         get_preferred_link= await s3Bucket.s3_get_presigned_link(i2.picture_cover)
    #         i2.picture_cover= get_preferred_link

    #         get_preferred_link= await s3Bucket.s3_get_presigned_link(i2.file_model)
    #         i2.file_model= get_preferred_link

    #     object_to_json_list.append(object_to_json)
    # return (object_to_json_list)





async def get_user(username, db):
    get_admin_id= db.query(models.Users).filter(models.Users.username==username.lower())

    if not get_admin_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Your account does not exist or has been removed")
    
    if get_admin_id.first().role == "user":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to view this content")
    
    if get_admin_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if not get_admin_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this username: '{username.lower()}' does not exist or has been removed")

    return get_admin_id.first()


async def get_user_by_username(user_username, username, db):
    get_admin_id= db.query(models.Users).filter(models.Users.username==username.lower())

    if not get_admin_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Your account does not exist or has been removed")
    
    if get_admin_id.first().role == "admin" or get_admin_id.first().role == "user":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to perform this operation")
    
    if get_admin_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account has been deactivated, please send us mail in the contact centre to access your account")

    get_admin_user_id= db.query(models.Users).filter(models.Users.id==id)
    if not get_admin_user_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Admin with this id: '{id}' does not exist or has been removed")


    return db.query(models.Users).filter(models.Users.username== user_username.lower()).first()




async def toggle_activation(db, username):
    get_admin_id= db.query(models.Users).filter(models.Users.username==username.lower())

    if get_admin_id.first().role == "superuser":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= f"Super Admin can not be deactivated")

    if get_admin_id.first().role == "admin" or get_admin_id.first().role == "user":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to perform this operation")

    if not get_admin_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"This account has been removed")
    
    if get_admin_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")


    
    get_student= db.query(models.Users).filter(models.Users.id== get_admin_id.first().id)
    toggle= "true"
    if get_admin_id.first().activated== "true":
        toggle= "false"
    toggle_activation_update= {
        "activated": toggle
    }
    get_admin_id.update(toggle_activation_update), get_student.update(toggle_activation_update)
    db.commit()

    if toggle== "false":
        return Response(content= f"The user with the id: {get_admin_id.first().id} was deactivated successfuly")
    
    return Response(content= f"The user with the id: {get_admin_id.first().id} was activated successfuly")



async def delete_admin(ids, username, db):
    get_admin_id= db.query(models.Users).filter(models.Users.username==username.lower())

    if not get_admin_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Your account has been removed")
    
    if get_admin_id.first().role == "admin" or get_admin_id.first().role == "user":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to perform this operation")
    
    if get_admin_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if not get_admin_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Admin with this username: '{username.lower()}' does not exist or has been removed")
    
    for id in ids:
        admin= db.query(models.Users).filter(models.Users.id== id)
        if admin.first().id == get_admin_id.first().id:
            raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Super Admin can not be deleted")
        if not admin.first():
            raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Admin with this id: '{id}' does not exist or has been removed")

        admin.delete(synchronize_session= False)
        db.commit()