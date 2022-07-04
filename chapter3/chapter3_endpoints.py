from enum import Enum
from typing import List
from fastapi import FastAPI, Path, Query, Body, Form, File, UploadFile
from pydantic import BaseModel


app = FastAPI()
LICENSE_REGEX = r"^\w{2}-\d{3}-\w{2}$"


class UserType(str, Enum):
    STANDARD = "standard"
    ADMIN = "admin"


class UsersFormat(str, Enum):
    SHORT = "short"
    FULL = "full"


class User(BaseModel):
    name: str
    age: int


class Company(BaseModel):
    name: str

################################################################
# Hello World
################################################################


@app.get("/chapter3_first_endpoint_01")
async def hello_world():
    return {"hello": "world"}


################################################################
# Path Parameters
################################################################


@app.get("/chapter3_path_parameters_01/users/{id}")
async def get_user(id: int):
    return {"id": id}


@app.get("/chapter3_path_parameters_03/users/{type}/{id}")
async def get_user(type: UserType, id: int):
    return {"type": type, "id": id}


@app.get("/chapter3_path_parameters_04/users/{id}")
async def get_user(id: int = Path(..., ge=1)):
    return {"id": id}


@app.get("/chapter3_path_parameters_05/license-plates/{license}")
async def get_license_plate(license: str = Path(..., min_length=9, max_length=9)):
    return {"license": license}


@app.get("/chapter3_path_parameters_06/license-plates/{license}")
async def get_license_plate(license: str = Path(..., regex=LICENSE_REGEX)):
    return {"license": license}

################################################################
# Query Parameters
################################################################


@app.get("/chapter3_query_parameters_01/users")
async def get_user(page: int = 1, size: int = 10):
    return {"page": page, "size": size}


@app.get("/chapter3_query_parameters_02/users")
async def get_user(format: UsersFormat):
    return {"format": format}


@app.get("/chapter3_query_parameters_03/users")
async def get_user(
    page: int = Query(1, gt=0),
    size: int = Query(10, le=100)
):
    return {"page": page, "size": size}

################################################################
# The request body
################################################################


@app.post("/chapter3_request_body_01/users")
async def create_user(name: str = Body(...),  age: int = Body(...)):
    return {"name": name, "age": age}


@app.post("/chapter3_request_body_02/users")
async def create_user(user: User):
    return user


@app.post("/chapter3_request_body_03/users")
async def create_user(user: User, company: Company):
    return {"user": user, "company": company}


@app.post("/chapter3_request_body_04/users")
async def create_user(user: User, priority: int = Body(..., ge=1, le=3)):
    return {"user": user, "priority": priority}


################################################################
# Form data and file uploads
################################################################


@app.post("/chapter3_form_data_01/users")
async def create_user(name: str = Form(...), age: int = Form(...)):
    return {"name": name, "age": age}


@app.post("/chapter3_file_uploads_01/files")
async def upload_file(file: bytes = File(...)):
    return {"file_size": len(file)}


@app.post("/chapter3_file_uploads_02/files")
async def upload_file(file: UploadFile = File(...)):
    return {
        "file_name": file.filename,
        "content_type": file.content_type
    }


@app.post("/chapter3_file_uploads_03/files")
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    return [
        {
            "file_name": file.filename,
            "content_type": file.content_type
        }
        for file in files
    ]
