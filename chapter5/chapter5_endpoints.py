from typing import Optional, Tuple
from fastapi import (
    FastAPI, APIRouter, HTTPException, status,
    Depends, Header, Query
)
from .chapter5_models import Post, DummyDatabase, PostUpdate


##############################################
# Dependencies
##############################################


async def simple_pagination(skip: int = 0, limit: int = 10) -> Tuple[int, int]:
    return (skip, limit)


async def complex_pagination(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=0),
) -> Tuple[int, int]:
    capped_limit = min(100, limit)
    return (skip, capped_limit)


async def get_post_or_404(id: int) -> Post:
    try:
        return db.posts[id]
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


def secret_header(secret_header: Optional[str] = Header(None)) -> None:
    """
    Function applied to a whole router.
    """
    if not secret_header or secret_header != "SECRET_VALUE":
        raise HTTPException(status.HTTP_403_FORBIDDEN)


def rate_limiter() -> None:
    """
    Function applied to the whole app, not implemented
    """
    return


class SimplePagination:
    def __init__(self, maximum_limit: int = 100) -> None:
        self.maximum_limit = maximum_limit

    async def __call__(
        self,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=0),
    ) -> Tuple[int, int]:
        capped_limit = min(self.maximum_limit, limit)
        return (skip, capped_limit)


class ComplexPagination:
    def __init__(self, maximum_limit: int = 100) -> None:
        self.maximum_limit = maximum_limit

    async def skip_limit(
        self,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=0),
    ) -> Tuple[int, int]:
        capped_limit = min(self.maximum_limit, limit)
        return (skip, capped_limit)

    async def page_size(
        self,
        page: int = Query(1, ge=1),
        size: int = Query(10, ge=0),
    ) -> Tuple[int, int]:
        capped_size = min(self.maximum_limit, size)
        return (page, capped_size)


##############################################
# Endpoints
##############################################


router = APIRouter(dependencies=[Depends(secret_header)])


@router.get("/chapter5_router_dependency_01/route1")
async def router_route1():
    return {"route": "route1"}


@router.get("/chapter5_router_dependency_01/route2")
async def router_route2():
    return {"route": "route2"}


db = DummyDatabase()
db.posts = {
    1: Post(id=1, title="Post 1", content="Content 1"),
    2: Post(id=2, title="Post 2", content="Content 2"),
    3: Post(id=3, title="Post 3", content="Content 3"),
}

simple_pagination_obj = SimplePagination(maximum_limit=50)
complex_pagination_obj = ComplexPagination(maximum_limit=50)


app = FastAPI(dependencies=[Depends(rate_limiter)])
app.include_router(router, prefix="/router")


@app.get("/chapter5_function_dependency_01/items")
async def list_items(p: Tuple[int, int] = Depends(simple_pagination)):
    skip, limit = p
    return {"skip": skip, "limit": limit}


@app.get("/chapter5_function_dependency_01/things")
async def list_things(p: Tuple[int, int] = Depends(simple_pagination)):
    skip, limit = p
    return {"skip": skip, "limit": limit}


@app.get("/chapter5_function_dependency_02/items")
async def list_items(p: Tuple[int, int] = Depends(complex_pagination)):
    skip, limit = p
    return {"skip": skip, "limit": limit}


@app.get("/chapter5_function_dependency_02/things")
async def list_things(p: Tuple[int, int] = Depends(complex_pagination)):
    skip, limit = p
    return {"skip": skip, "limit": limit}


@app.get("/chapter5_function_dependency_03/posts/{id}")
async def get(post: Post = Depends(get_post_or_404)):
    return post


@app.patch("/chapter5_function_dependency_03/posts/{id}")
async def update(post_update: PostUpdate, post: Post = Depends(get_post_or_404)):
    updated_post = post.copy(update=post_update.dict())
    db.posts[post.id] = updated_post
    return updated_post


@app.delete(
    "/chapter5_function_dependency_03/posts/{id}", 
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete(post: Post = Depends(get_post_or_404)):
    db.posts.pop(post.id)


@app.get("/chapter5_class_dependency_01/items")
async def list_items(p: Tuple[int, int] = Depends(simple_pagination_obj)):
    skip, limit = p
    return {"skip": skip, "limit": limit}


@app.get("/chapter5_class_dependency_01/things")
async def list_things(p: Tuple[int, int] = Depends(simple_pagination_obj)):
    skip, limit = p
    return {"skip": skip, "limit": limit}


@app.get("/chapter5_class_dependency_02/items")
async def list_items(p: Tuple[int, int] = Depends(complex_pagination_obj.skip_limit)):
    skip, limit = p
    return {"skip": skip, "limit": limit}


@app.get("/chapter5_class_dependency_02/things")
async def list_things(p: Tuple[int, int] = Depends(complex_pagination_obj.page_size)):
    page, size = p
    return {"page": page, "size": size}


@app.get(
    "/chapter5_path_dependency_01/protected-route", 
    dependencies=[Depends(secret_header)]
)
async def protected_route():
    return {"hello": "world"}

