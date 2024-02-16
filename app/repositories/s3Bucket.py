import boto3
from loguru import logger
import os
from fastapi.responses import FileResponse
import os
from fastapi import status, Response, HTTPException
from dotenv import load_dotenv
from .import file_names_processing
from typing import Optional
from PIL import Image, ImageOps

load_dotenv()

s3= boto3.resource(
    service_name= "s3",
    # region_name= "eu-north-1",
    region_name= "us-east-1",
    aws_access_key_id= os.getenv("aws_access_key_id"),
    aws_secret_access_key= os.getenv("aws_secret_access_key")
    )

# S3_BUCKET_NAME= "environmental-mapping-bucket"
S3_BUCKET_NAME= "emp-bucket-new"
bucket= s3.Bucket(S3_BUCKET_NAME)
#bucket_folder_path= "images"

session= boto3.session.Session()
s3_client= session.client(
    's3',
    aws_access_key_id= os.getenv("aws_access_key_id"),
    aws_secret_access_key= os.getenv("aws_secret_access_key")
)

def id_folder_split(id):
    return os.path.splitext(id)[0]



UPLOAD_DIR= os.path.join("app/media")
file_extensions= [".gltf", ".glb", ".fbx", ".stl", ".obj", ".dae", ".ifc"]
async def s3_upload_model(folder_id, folder_path):
    try:
        model_name_and_path= None
        for root, dirs, files in os.walk(folder_path):
            # print("Here")
            # print(files)
            # print("Down")
            for file_name in files:
                local_file_path = os.path.join(root, file_name)
                filename_and_path= f"{folder_id}/{local_file_path}"
                filename_and_path= filename_and_path.replace('\\', '/')
                # print(filename_and_path)
                logger.info(f"Uploading {local_file_path} to s3")
                s3_client.upload_file(local_file_path, S3_BUCKET_NAME, filename_and_path)
                if os.path.splitext(filename_and_path.split('\\')[0])[1] in file_extensions:
                    model_name_and_path= filename_and_path

        if model_name_and_path:
            aws_access_link= f"https://environmental-mapping-bucket-new.s3.amazonaws.com/{model_name_and_path}"
            return aws_access_link
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail= "Could not upload model file, something went wrong, also make sure you have good internet connection.")
 
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail= "Could not upload model file, something went wrong, also make sure you have good internet connection.")




async def s3_upload_model_file_only(file, bucket_folder_path):
        s3_client.put_object(Bucket= S3_BUCKET_NAME, Key=f"{bucket_folder_path}/")

        bucket_folder_path= f"{bucket_folder_path}/model_file"
        filename= file.filename

        filename_and_path= f"{bucket_folder_path}/{filename}"

        logger.info(f"Uploading {filename_and_path} to s3")
        bucket.upload_fileobj(file.file, f"{filename_and_path}")

        aws_access_link= f"https://environmental-mapping-bucket-new.s3.amazonaws.com/{filename_and_path}"
        return aws_access_link





async def s3_upload(file, bucket_folder_path):
        s3_client.put_object(Bucket= S3_BUCKET_NAME, Key=f"{bucket_folder_path}/")

        bucket_folder_path= f"{bucket_folder_path}/picture_cover"
        filename= await file_names_processing.names_process(file)
        logger.info(f"Uploading {file.filename} to s3")


        filename_and_path= f"{bucket_folder_path}/{os.path.splitext(filename)[0]}.webp"
        #++++++IMAGE COMPRESSING BEFORE UPLOAD++++++++
        # Save the uploaded image to a temporary file
        save_filename= filename
        with open(save_filename, "wb") as image_file:
            image_file.write(file.file.read())

        # Compress the image to medium quality
        # img = Image.open(filename).convert("RGB")
        img = Image.open(save_filename)
        try:
            img= ImageOps.exif_transpose(img)
        except:
            pass
        img.save("compressed_img.webp", format="webp", quality=15)

        with open("compressed_img.webp", "rb") as file_c:
            file= file_c
            
            bucket.upload_fileobj(file, f"{filename_and_path}")
            #uploaded_file_url= f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{filename_and_path}" 
            # Clean up the temporary and compressed images
            os.remove(save_filename)
            os.remove("compressed_img.webp")

            aws_access_link= f"https://environmental-mapping-bucket-new.s3.amazonaws.com/{filename_and_path}"
            return aws_access_link
    # try:


    # except:
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail= "Could not upload picture cover, something went wrong, also make sure you have good internet connection.")



async def s3_upload_replacement(file, filename, bucket_folder_path, is_image):
    logger.info(f"Updating {filename} to s3")
    filename_and_path= f"{bucket_folder_path}/{filename}"

    if is_image:
        # filename= os.path.splitext(filename)[0] + '.jpg'

        #++++++IMAGE COMPRESSING BEFORE UPLOAD++++++++
        # Save the uploaded image to a temporary file
        save_filename= filename
        with open(save_filename, "wb") as image_file:
            image_file.write(file.file.read())

        # Compress the image to medium quality
        # img = Image.open(save_filename).convert("RGB")
        img = Image.open(save_filename)
        try:
            img= ImageOps.exif_transpose(img)
        except:
            pass
        # CONSTRAINING THE IMAGE SIZE TO 100 KB
        # image_size = img.size
        # image_width, image_height = image_size
        # target_size = 1000000  # Target size in bytes ( KB)
        # target_ratio = target_size / (image_width * image_height)
        # target_width = image_width * target_ratio
        # target_height = image_height * target_ratio
        # resized_image = img.resize((int(target_width), int(target_height)))

        # resized_image.save("compressed_img.jpg", format="webp", quality=100)

        img.save("compressed_img.webp", format="webp", quality=15)

        with open("compressed_img.webp", "rb") as file_c:
            file= file_c
            
            bucket.upload_fileobj(file, f"{filename_and_path}")
            # Clean up the temporary and compressed images
            os.remove(save_filename)
            os.remove("compressed_img.webp")
            return f"{os.path.splitext(filename)[0]}.webp"
    
    else:
        bucket.upload_fileobj(file.file, f"{filename_and_path}")
        return filename


    

async def s3_get_presigned_link(bucket_folder_path, file_name):
    logger.info(f"Getting link {file_name} to s3")
    filename_and_path= f"{bucket_folder_path}/{file_name}"
    
    uploaded_file_url= s3_client.generate_presigned_url(
        'get_object', 
        Params={'Bucket': S3_BUCKET_NAME, 'Key': filename_and_path},
        # ExpiresIn= 365 * 24 * 60 * 60 * 100  #100 days in seconds
        )
    return uploaded_file_url



async def s3_download(id, bucket_folder_path):
    filename_and_path= f"{bucket_folder_path}/{id}"
    default_filename= f"downloaded{os.path.splitext(id)[1]}"
    try:
        s3_client.download_file(f"{S3_BUCKET_NAME}", f"{filename_and_path}",f"{UPLOAD_DIR}/{default_filename}")
        return FileResponse(path=f"{UPLOAD_DIR}/{default_filename}", media_type="application/octet-stream", filename= id)
    except:
        
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Either this file is no more available or the name of this file you are trying to download does not exist, trying to download again could solve the problem")


async def s3_delete(id, bucket_folder_path):
    #id_folder= id_folder_split(id)
    filename_and_path= f"{bucket_folder_path}/{id}"
    try:
        s3.Object(bucket.name, filename_and_path).delete()
        return True
    except:
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not delete the initial file")
    







async def s3_get_presigned_link(filename_and_path):
    logger.info(f"Getting link {filename_and_path} to s3")
    
    uploaded_file_url= s3_client.generate_presigned_url(
        'get_object', 
        Params={'Bucket': S3_BUCKET_NAME, 'Key': filename_and_path},
        # ExpiresIn= 365 * 24 * 60 * 60 * 100  #100 days in seconds
        )
    return uploaded_file_url



