import os
import uuid
import time



timestr= time.strftime("%Y%m%d-%H%M%S")
async def names_process(file):   
    filename=f"{uuid.uuid4()}-{timestr}{os.path.splitext(file.filename)[1]}"     
    return  (filename)

