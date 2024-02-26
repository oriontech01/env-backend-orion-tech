from sqlalchemy import Column, Integer, String, ForeignKey
from .database import Base
from sqlalchemy.orm import relationship
import time

class Users(Base):
    __tablename__= "users"
    activated= Column(String, default= True)
    id= Column(Integer, primary_key=True, index= True)
    username= Column(String, unique=True)
    role= Column(String)
    password= Column(String)
    profile_picture= Column(String, default=None)
    registration_date= Column(String, default= time.strftime("%Y%m%d-%H%M%S"))
    
    user_models= relationship("ModelObject", back_populates="users")


class ModelObject(Base):
    __tablename__= "modelobject"
    date_and_time_of_sample= Column(String, default= time.strftime("%Y%m%d-%H%M%S"))
    id= Column(String, primary_key=True, index= True)
    description_model= Column(String)
    file_model= Column(String)
    picture_cover= Column(String)

    users_id= Column(Integer, ForeignKey('users.id'))
    users= relationship("Users", back_populates="user_models")

    objects_relationship= relationship("ObjectsData", back_populates="models_relationship")


class ObjectsData(Base):
    __tablename__= "objects_data"
    # name_of_tagger= Column(String)
    # location
    id= Column(Integer, primary_key=True, index= True)
    object_name= Column(String)
    listeria= Column(String)
    apc= Column(Integer)
    salmonella= Column(String)
    date_of_sample= Column(String)
    time_of_sample= Column(String)
    type_of_sample= Column(String)
    comment_box= Column(String)

    id_model= Column(String, ForeignKey('modelobject.id'))
    models_relationship= relationship("ModelObject", back_populates="objects_relationship")

