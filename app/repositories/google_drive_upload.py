from fastapi.responses import JSONResponse
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload, MediaFileUpload
import io
from loguru import logger
from PIL import Image, ImageOps
import os

from .import file_names_processing

SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'app/repositories/google-service-account.json'
PARENT_FOLDER_ID_MODEL = "1HSrklYTOoGxaIYynEfaYshbAO_M9_emM"
PARENT_FOLDER_ID_PICTURE = "1Nwa_wn-6WeftkpenKKtOQFMn7XV8marM"




async def authenticate():
    creds= service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return creds           








async def upload_folder_to_drive(folder_path, folder_name):
    creds= await authenticate()
    drive_service = build('drive', 'v3', credentials=creds)

    folder_path = folder_path


    # folder_metadata = {
    #     'name': folder_path,
    #     'parents': PARENT_FOLDER_ID_MODEL,
    #     'mimeType': 'application/vnd.google-apps.folder'
    # }
    # folder = drive_service.files().create(body=folder_metadata).execute()
    # folder_id= folder.get('id')

    folder_metadata = {
        'name': folder_name,
        'parents': PARENT_FOLDER_ID_MODEL,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = drive_service.files().create(body=folder_metadata).execute()
    folder_id= folder.get('id')

    permission = {
    'type': 'user',
    'role': 'owner',
    'emailAddress': 'environmental-service-account@environmental-cloud.iam.gserviceaccount.com',
    }

    # Apply permission grant to the folder
    drive_service.permissions().create(
        fileId=folder_id,
        body=permission,
        transferOwnership=True,
    ).execute()




        # file_metadata= {
        #     'name': filename,
        #     'parents': [PARENT_FOLDER_ID_MODEL]
        # }

        # # media= {'media': file.file}
        # media= MediaIoBaseUpload(file.file, mimetype=file.content_type, resumable= True)

        # file_upload= service.files().create(
        #     body= file_metadata,
        #     media_body= media,
        #     # fields='id'
        # ).execute()

    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            local_file_path = os.path.join(root, file_name)

            file_metadata = {
                'name': os.path.basename(local_file_path),
                'parents': [folder_id]
            }
            media = MediaFileUpload(local_file_path)
            file_upload = drive_service.files().create(body=file_metadata, media_body=media).execute()
            print(file_upload["id"])


    print(f"Folder '{folder_path}' uploaded to Google Drive")








# Delete a file
async def delete_file(file_id):
    try:
        creds= await authenticate()
        service= build('drive', 'v3', credentials= creds)

        res= service.files().delete(fileId=file_id).execute()
        print(res)
        logger.log(f'File {file_id} deleted successfully')
        return res
    except:
        pass


async def download_file(file_id):
    creds= await authenticate()
    service= build('drive', 'v3', credentials= creds)

    request = service.files().get_media(fileId=file_id)
    file_handle = io.BytesIO()
    downloader = MediaIoBaseDownload(file_handle, request)
    
    done = False
    while not done:
        _, done = downloader.next_chunk()

    file_handle.seek(0)

    base64_data = file_handle.read().encode("base64").decode("utf-8")
    return {"image_data": base64_data}
    # return JSONResponse(content={"file_id": file_id, "image_data": base64_data})
    # return file_handle



async def upload_model(file, is_image):
    filename= await file_names_processing.names_process(file)

    creds= await authenticate()
    service= build('drive', 'v3', credentials= creds)


    if is_image:
            save_filename= filename
            filename= f"{os.path.splitext(filename)[0]}.webp"

            async def start_upload(file):
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
                    
                    file_metadata= {
                        'name': filename,
                        'parents': [PARENT_FOLDER_ID_PICTURE]
                    }

                    # media= {'media': file.file}
                    media= MediaIoBaseUpload(file, mimetype="image/webp", resumable= True)

                    file_upload= service.files().create(
                        body= file_metadata,
                        media_body= media,
                        # fields='id'
                    ).execute()
                    
                    return file_upload

            file_upload= await start_upload(file)
            os.remove(save_filename)
            os.remove("compressed_img.webp")

            return f"https://drive.google.com/uc?export=view&id={file_upload['id']}"
            
    else:
        file_metadata= {
            'name': filename,
            'parents': [PARENT_FOLDER_ID_MODEL]
        }

        # media= {'media': file.file}
        media= MediaIoBaseUpload(file.file, mimetype=file.content_type, resumable= True)

        file_upload= service.files().create(
            body= file_metadata,
            media_body= media,
            # fields='id'
        ).execute()

        return f"https://drive.google.com/uc?export=view&id={file_upload['id']}"

    


# def upload_model(file_path, model_name):
#     creds= authenticate()
#     service= build('drive', 'v3', credentials= creds)

#     file_metadata= {
#         'name': model_name,
#         'parents': [PARENT_FOLDER_ID_MODEL]
#     }

#     file_path= service.files().create(
#         body= file_metadata,
#         media_body= file_path
#     ).execute()
