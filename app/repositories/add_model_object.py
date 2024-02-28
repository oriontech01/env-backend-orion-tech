from .. import models
from .import s3Bucket
from ..hashing import Hash
# from ..routers import otp_management
from fastapi import HTTPException, status, Response
import os, shutil
from dotenv import load_dotenv

import io, zipfile

load_dotenv()




async def add_model(request, picture_cover, model_object, username, db):
    get_admin_id= db.query(models.Users).filter(models.Users.username==username.lower())

    if get_admin_id.first().role == "user":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to perform this operation")

    if not get_admin_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"This account does not exist or has been deactivated")




    try:
        shutil.rmtree('model')
    except: pass    

    upload_picture_cover= await s3Bucket.s3_upload(picture_cover, request.id)

    upload_model= None
    if os.path.splitext(model_object.filename)[1] != ".zip":
        upload_model= await s3Bucket.s3_upload_model_file_only(model_object, request.id)
    else:
        with zipfile.ZipFile(io.BytesIO(model_object.file.read()), 'r') as zip_ref:
            # Create a temporary directory to extract files
            temp_dir = f'./model'
            os.makedirs(temp_dir, exist_ok=True)

            # Extract all files from the zip archive
            zip_ref.extractall(temp_dir)

            model_folder_path = os.path.relpath(temp_dir)

            upload_model= await s3Bucket.s3_upload_model(request.id, model_folder_path)
    
            # upload_model= await google_drive_upload.upload_folder_to_drive(model_folder_path, request.id)

        # with zipfile.ZipFile(io.BytesIO(model_object.file.read()), 'r') as zip_ref:
        #     # Upload each extracted file to S3 (example using boto3)

        #     for file_info in zip_ref.infolist():
        #         # Extract the file content into memory
        #         file_content = zip_ref.read(file_info.filename)
        #         # print(file_content)

        try:
            shutil.rmtree(request.id)
        except: pass
    
    if (upload_model == None):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not finalize the model file upload")

    # upload_model= '79136187963892hkfqd'
    # upload_picture_cover= 'dfkjdcd79136187963892hkfqd'
    new_model= models.ModelObject(id= request.id.upper(), 
                            description_model= request.description_model, 
                            file_model= upload_model, 
                            picture_cover= upload_picture_cover, 
                            users_id= get_admin_id.first().id
                            )
    db.add(new_model)
    db.commit()
    db.refresh(new_model)

    # for i in request.objects_data:
    #     new_object_data= models.ObjectsData(
    #         object_name= i.object_name, 
    #         listeria= i.listeria, 
    #         apc= i.apc, 
    #         salmonella= i.salmonella, 
    #         date_of_sample= i.date_of_sample,
    #         time_of_sample= i.time_of_sample, 
    #         type_of_sample= i.type_of_sample, 
    #         comment_box= i.comment_box, 
    #         id_model= request.id.upper()
    #         )
    #     db.add(new_object_data)
    #     db.commit()
    #     db.refresh(new_object_data)
    
    return Response(status_code=status.HTTP_201_CREATED)






async def object_add_model(request, username, db):
    get_admin_id= db.query(models.Users).filter(models.Users.username==username.lower())

    if get_admin_id.first().role == "user":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to perform this operation")

    check_db= db.query(models.ModelObject).filter(models.ModelObject.id == request.id)
    if not check_db.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Model with this name: '{request.id}' does not exist or has been deleted.")
    
    # if (get_admin_id.first().role != "super_user" and check_db.first().users_id != get_admin_id.first().id):
    #     raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= f"Admin with this username: '{username.lower()}' can not perform this operation")


    if not get_admin_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"This account does not exist or has been deactivated")

    for i in request.objects_data:
        r_comment_box= i.comment_box
        r_type_of_sample= i.type_of_sample
        r_time_of_sample= i.time_of_sample
        r_date_of_sample= i.date_of_sample
        r_salmonella= i.salmonella
        r_apc= i.apc
        r_listeria= i.listeria

        if r_comment_box == "":
            r_comment_box= ""
        
        if r_type_of_sample == "":
            r_type_of_sample= ""
        
        if r_time_of_sample == "":
            r_time_of_sample= ""
        
        if r_date_of_sample == "":
            r_date_of_sample= ""
        
        if r_salmonella == "":
            r_salmonella= ""
        
        if r_apc == "":
            r_apc= 0
        
        if r_listeria == "":
            r_listeria= ""

        

        new_object_data= models.ObjectsData(
            # object_name= i.object_name.title(),
            object_name= i.object_name, 
            listeria= r_listeria, 
            apc= int(r_apc), 
            salmonella= r_salmonella, 
            date_of_sample= r_date_of_sample,
            time_of_sample= r_time_of_sample, 
            type_of_sample= r_type_of_sample, 
            comment_box= r_comment_box, 
            id_model= request.id
            )
        db.add(new_object_data)
        db.commit()
        db.refresh(new_object_data)
    
    return Response(status_code=status.HTTP_201_CREATED)
    


async def update_model_super_admin(request, picture_cover, username, db):
    get_admin_id= db.query(models.Users).filter(models.Users.username==username.lower())

    if get_admin_id.first().role == "user":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to perform this operation")

    if not get_admin_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"This account does not exist or has been deactivated")

    model_= db.query(models.ModelObject).filter(models.ModelObject.id== request.id)
    if not model_.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"This model does not exist or has been removed")


    #+++++++ FILTERING OUT THE NONE FIELDS
        # ++++++ COVER PICTURE FILE +++++++++
    if picture_cover != None:
        extract_picture_id= model_.first().picture_cover.split('=')[-1]
        
        upload_picture_cover= ''
        model_.update({"picture_cover": upload_picture_cover})
        db.commit()


    new_model= {}
    if request.description_model != None and request.description_model != "":
        model_.update({"description_model": request.description_model})
        db.commit()

    if request.objects_data != [] and request.objects_data != None:
        for i in request.objects_data:
            new_objects_data= {}
            for i2 in i:
                if i2[1] is not None:
                    new_objects_data.setdefault(i2[0], i2[1])
            
            objects_data= db.query(models.ObjectsData).filter(models.ObjectsData.id== int(new_objects_data['id']))
            if not objects_data.first():
                raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Object Data with this id: '{new_objects_data['id']}' does not exist or has been removed")
            
            new_objects_data['object_name']= new_objects_data['object_name'].title()
            objects_data.update(new_objects_data)
            db.commit()
    



async def update_model_admin(request, picture_cover, username, db):
    get_admin_id= db.query(models.Users).filter(models.Users.username==username.lower())

    if get_admin_id.first().role == "user":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to perform this operation")

    if not get_admin_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"This account does not exist or has been deactivated")

    model_= db.query(models.ModelObject).filter(models.ModelObject.id== request.id)
    if not model_.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"This model does not exist or has been removed")
    
    if model_.first().users_id != get_admin_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Object Data with this id: '{model_.first().id}' could not be matched with any of your model")


    #+++++++ FILTERING OUT THE NONE FIELDS
        # ++++++ COVER PICTURE FILE +++++++++
    if picture_cover != None:
        extract_picture_id= model_.first().picture_cover.split('=')[-1]
       
    
        upload_picture_cover= ''
        model_.update({"picture_cover": upload_picture_cover})
        db.commit()


    new_model= {}
    if request.description_model != None and request.description_model != "":
        model_.update({"description_model": request.description_model})
        db.commit()

    if request.objects_data != [] and request.objects_data != None:
        for i in request.objects_data:
            new_objects_data= {}
            for i2 in i:
                if i2[1] is not None:
                    new_objects_data.setdefault(i2[0], i2[1])
            
            objects_data= db.query(models.ObjectsData).filter(models.ObjectsData.id== int(new_objects_data['id']))
            if not objects_data.first():
                raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Object Data with this id: '{new_objects_data['id']}' does not exist or has been removed")
            
            new_objects_data['object_name']= new_objects_data['object_name'].title()
            objects_data.update(new_objects_data)
            db.commit()




async def delete_model_super_admin(id_list, username, db):
    get_admin_id= db.query(models.Users).filter(models.Users.username==username.lower())

    if not get_admin_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Your account has been removed")
    
    if get_admin_id.first().role == "user":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to perform this operation")
    
    if get_admin_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if not get_admin_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Admin with this username: '{username.lower()}' does not exist or has been removed")
    

    for id in id_list:
        models_= db.query(models.ModelObject).filter(models.ModelObject.id== id)

        if get_admin_id.first().role != "superuser" :
            raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to perform this operation")
    

        if not models_.first():
            raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Model with this id: '{id}' does not exist or has been removed")

        object_data= db.query(models.ObjectsData).filter(models.ObjectsData.id_model== id)
        if object_data.first():
            object_data.delete(synchronize_session= False)

        extract_model_id= models_.first().file_model.split('=')[-1]
        extract_picture_id= models_.first().picture_cover.split('=')[-1]
       

        models_.delete(synchronize_session= False)
        db.commit()


async def delete_object_super_admin(id_list, username, db):
    get_admin_id= db.query(models.Users).filter(models.Users.username==username.lower())


    if not get_admin_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Your account has been removed")
    
    if get_admin_id.first().role == "admin" or get_admin_id.first().role == "user":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to perform this operation")
    
    if get_admin_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if not get_admin_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Admin with this username: '{username.lower()}' does not exist or has been removed")
    

    for id in id_list:
        object_data= db.query(models.ObjectsData).filter(models.ObjectsData.id== id)
        if not object_data.first():
            raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Object with this id: '{id}' does not exist or has been removed")

        object_data.delete(synchronize_session= False)
        db.commit()





async def delete_model_admin(id_list, username, db):
    get_admin_id= db.query(models.Users).filter(models.Users.username==username.lower())

    if get_admin_id.first().role == "user":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to perform this operation")

    if not get_admin_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Your account has been removed")
    
    if get_admin_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if not get_admin_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Admin with this username: '{username.lower()}' does not exist or has been removed")
    
    models_= db.query(models.ModelObject).filter(models.ModelObject.users_id== get_admin_id.first().id).filter(models.ModelObject.id== id)
    if not models_.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Model with this id: '{id}' does not exist or has been removed")
    if models_.first().users_id != get_admin_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Model with this id: '{id}' could not be matched with any of your model")


    for id in id_list:
        object_data= db.query(models.ObjectsData).filter(models.ObjectsData.id_model== id)
        if object_data.first():
            object_data.delete(synchronize_session= False)

        extract_model_id= models_.first().file_model.split('=')[-1]
        extract_picture_id= models_.first().picture_cover.split('=')[-1]
        

        models_.delete(synchronize_session= False)
        db.commit()


async def delete_object_admin(id_list, username, db):
    get_admin_id= db.query(models.Users).filter(models.Users.username==username.lower())

    if get_admin_id.first().role == "user":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to perform this operation")

    if not get_admin_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Your account has been removed")
    
    if get_admin_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if not get_admin_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Admin with this username: '{username.lower()}' does not exist or has been removed")
    
    for id in id_list:
        object_data= db.query(models.ObjectsData).filter(models.ObjectsData.id== id)
        if not object_data.first():
            raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Object with this id: '{id}' does not exist or has been removed")
        
        models_= db.query(models.ModelObject).filter(models.ModelObject.users_id== get_admin_id.first().id).filter(models.ModelObject.id== object_data.first().id_model)
        if not models_.first():
            raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Object with this id: '{id}' could not be matched with any of your model")


        object_data.delete(synchronize_session= False)
        db.commit()