from pydantic import BaseModel, Field
from typing import List, Optional
from pydantic.types import constr



class TokenDataUser(BaseModel):
    username: Optional[str]= None

class SignUp(BaseModel):
    username: str
    role: str
    password: str


class RoleUpdate(BaseModel):
    id: int
    role: str



class ModelObjectBase(BaseModel):
    date_and_time_of_sample: str
    id: str
    description_model: str
    file_model: str
    picture_cover: str

    class Config():
        from_attributes= True

        

class ObjectsData(BaseModel):
    id: int
    object_name: str
    listeria: str
    apc: int
    salmonella: str
    date_of_sample: str
    time_of_sample: str
    type_of_sample: str
    comment_box: str

    id_model: str
    models_relationship: ModelObjectBase
    
    class Config():
        from_attributes= True




class UsersBase(BaseModel):
    id: int
    activated: str
    registration_date: str
    username: str
    
    class Config():
        from_attributes= True


class HomeModelObjects(BaseModel):
    date_and_time_of_sample: str
    id: str
    description_model: str
    file_model: str
    picture_cover: str
    objects_relationship: List[ObjectsData]

    users: UsersBase

    class Config():
        from_attributes= True

class ModelObject(ModelObjectBase):   
    users_id: str
    users: UsersBase

    objects_relationship: List[ObjectsData]= []

    class Config():
        from_attributes= True


class ModelObjectUser(ModelObjectBase):   
    objects_relationship: List[ObjectsData]= []

class Users(BaseModel):
    id: int
    activated: str
    registration_date: str
    username: str
    role: str
    profile_picture: Optional[str]= None

    user_models: List[ModelObjectUser]
    
    class Config():
        from_attributes= True





#++++++++++++++++++++ FORMS ++++++++++++++++++++++
class ObjectsDataForm(BaseModel):
    object_name: Optional[str]= None
    listeria: Optional[str]= None
    apc: Optional[str]= None
    salmonella: Optional[str]= None
    date_of_sample: Optional[str]= None
    time_of_sample: Optional[str]= None
    type_of_sample: Optional[str]= None
    comment_box: Optional[str]= None
    
    class Config():
        from_attributes= True

class ModelObjectForm(BaseModel):   
    id: str
    description_model: str
    objects_data: List[ObjectsDataForm]= None

    class Config():
        from_attributes= True


class ModelObjectFormModfied(BaseModel):   
    id: str
    description_model: str

    class Config():
        from_attributes= True


class ObjectModelObjectForm(BaseModel):   
    id: str
    objects_data: List[ObjectsDataForm]= None

    class Config():
        from_attributes= True



class ObjectsDataFormUpdate(ObjectsDataForm):
    id:int


class ModelObjectFormUpdate(BaseModel):   
    id: str
    description_model: Optional[str]= None
    objects_data: List[ObjectsDataFormUpdate]= None

    class Config():
        from_attributes= True

# class ModelObjectFormUpdate(BaseModel):   
#     id: str
#     description_model: str
#     objects_data: List[ObjectsDataFormUpdate]= None

#     class Config():
#         from_attributes= True
