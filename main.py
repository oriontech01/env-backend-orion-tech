from fastapi import FastAPI, status, Response
from app.database import engine
from app import  models
from app.routers import admin, admin_model_object, authentication, home_models
from fastapi.middleware.cors import CORSMiddleware

#USING THIS PORT TO RUN IT WILL MAKE THE APP LISTEN TO ALL ADDRESS THAT ARE AVAILABLE FOR ALLOCATION BY COMPUTER 
#THIS IS ALSO USEFUL WHEN CONNECTING LOCALLY FROM A LOCAL DEVICE IN FLUTTER TO THE API
#uvicorn main:app --host 0.0.0.0 --port 8000    WHILE FOR THE EMULATOR ANDROID ADDRESS "10.0.2.2:8000"
# uvicorn main:app --host 0.0.0.0 --port 443  
#Noctis high contrast  MY VS CODE THEME

app=FastAPI()
origins = ["http://localhost:3000", "http://ec2-174-129-80-5.compute-1.amazonaws.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers= ["*"]
)

models.Base.metadata.create_all(engine)

app.include_router(home_models.router)
app.include_router(admin.router)
app.include_router(admin_model_object.router)
app.include_router(authentication.router)



@app.get('/', status_code=status.HTTP_200_OK)
def home_models():
    return Response(content= "This is ENVIRONMENTAL API, contact the organisation for the routers available!")
