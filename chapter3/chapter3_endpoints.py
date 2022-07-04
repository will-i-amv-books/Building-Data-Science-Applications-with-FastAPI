import os
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel
from fastapi import (
    FastAPI, Form, File, Path, Query, Header, Cookie, Body,
    status, Request, Response, UploadFile, HTTPException
)
from fastapi.responses import (
    HTMLResponse, PlainTextResponse, RedirectResponse, FileResponse
)


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


class Post(BaseModel):
    title: str


class PrivatePost(BaseModel):
    title: str
    nb_views: int


class PublicPost(BaseModel):
    title: str


posts = {1: PrivatePost(title="Hello", nb_views=100)}  # Dummy database


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


################################################################
# Headers and cookies
################################################################


@app.get("/chapter3_headers_cookies_01")
async def get_header(hello: str = Header(...)):
    return {"hello": hello}


@app.get("/chapter3_headers_cookies_02")
async def get_header(user_agent: str = Header(...)):
    return {"user_agent": user_agent}


@app.get("/chapter3_headers_cookies_03")
async def get_cookie(hello: Optional[str] = Cookie(None)):
    return {"hello": hello}


@app.get("/chapter3_request_object_01")
async def get_request_object(request: Request):
    return {"path": request.url.path}


################################################################
# Path operation parameters
################################################################


@app.post(
    "/chapter3_response_path_parameters_01/posts",
    status_code=status.HTTP_201_CREATED
)
async def create_post(post: Post):
    return post


@app.get("/chapter3_response_path_parameters_02")
async def custom_cookie(response: Response):
    response.set_cookie("cookie-name", "cookie-value", max_age=86400)
    return {"hello": "world"}


@app.delete(
    "/chapter3_response_path_parameters_02/posts/{id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_post(id: int):
    posts.pop(id, None)
    return None


@app.get("/chapter3_response_path_parameters_03/posts/{id}")
async def get_post(id: int):
    return posts[id]


@app.get(
    "/chapter3_response_path_parameters_04/posts/{id}",
    response_model=PublicPost
)
async def get_post(id: int):
    return posts[id]


################################################################
# The response parameter
################################################################


@app.get("/chapter3_response_parameter_01")
async def custom_header(response: Response):
    response.headers["Custom-Header"] = "Custom-Header-Value"
    return {"hello": "world"}


@app.get("/chapter3_response_parameter_02")
async def custom_cookie(response: Response):
    response.set_cookie("cookie-name", "cookie-value", max_age=86400)
    return {"hello": "world"}


@app.put("/chapter3_response_parameter_03/posts/{id}")
async def update_or_create_post(id: int, post: Post, response: Response):
    if id not in posts:
        response.status_code = status.HTTP_201_CREATED
    posts[id] = post
    return posts[id]


################################################################
# Raising HTTP errors
################################################################


@app.post("/chapter3_raise_errors_01/password")
async def check_password(
    password: str = Body(...),
    password_confirm: str = Body(...)
):
    if password != password_confirm:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Passwords don't match.",
        )
    return {"message": "Passwords match."}


@app.post("/chapter3_raise_errors_02/password")
async def check_password(
    password: str = Body(...),
    password_confirm: str = Body(...)
):
    if password != password_confirm:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Passwords don't match.",
                "hints": [
                    "Check the caps lock on your keyboard",
                    "Make the password visible by clicking on the eye icon",
                ],
            },
        )
    return {"message": "Passwords match."}


################################################################
# Building a custom response
################################################################


@app.get("/chapter3_custom_response_01/html", response_class=HTMLResponse)
async def get_html():
    return (
        """
        <html>
            <head>
                <title>Hello world!</title>
            </head>
            <body>
                <h1>Hello world!</h1>
            </body>
        </html>
        """
    )


@app.get("/chapter3_custom_response_01/text", response_class=PlainTextResponse)
async def text():
    return "Hello world!"


@app.get("/chapter3_custom_response_02/redirect")
async def redirect():
    return RedirectResponse("/redirected-url")


@app.get("/chapter3_custom_response_03/redirect")
async def redirect():
    return RedirectResponse(
        "/redirected-url",
        status_code=status.HTTP_301_MOVED_PERMANENTLY
    )


@app.get("/redirected-url")
async def redirected():
    return


@app.get("/chapter3_custom_response_04/cat")
async def get_cat():
    root_directory = os.path.dirname(os.path.dirname(__file__))
    picture_path = os.path.join(root_directory, "assets", "cat.jpg")
    return FileResponse(picture_path)


@app.get("/chapter3_custom_response_05/xml")
async def get_xml():
    content = (
        """
        <?xml version="1.0" encoding="UTF-8"?>
        <Hello>World</Hello>
        """
    )
    return Response(content=content, media_type="application/xml")

