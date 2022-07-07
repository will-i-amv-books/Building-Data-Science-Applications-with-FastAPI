from typing import List, Mapping, Tuple, cast
from databases import Database
from fastapi import Depends, FastAPI, HTTPException, Query, status
from database import get_database, sqlalchemy_engine
from models import (
    comments,
    metadata,
    posts,
    CommentCreate,
    CommentDB,
    PostDB,
    PostCreate,
    PostPartialUpdate,
    PostPublic,
)


app = FastAPI()


@app.on_event("startup")
async def startup():
    await get_database().connect()
    metadata.create_all(sqlalchemy_engine)


@app.on_event("shutdown")
async def shutdown():
    await get_database().disconnect()


async def pagination(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=0),
) -> Tuple[int, int]:
    capped_limit = min(100, limit)
    return (skip, capped_limit)


async def get_post_or_404(
    id: int, database: Database = Depends(get_database)
) -> PostPublic:
    raw_post = await database.fetch_one(
        posts
        .select()
        .where(posts.c.id == id)
    )
    if raw_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    raw_comments = await database.fetch_all(
        comments
        .select()
        .where(comments.c.post_id == id)
    )
    comments_list = [CommentDB(**comment) for comment in raw_comments]

    return PostPublic(**raw_post, comments=comments_list)


@app.get("/posts")
async def list_posts(
    pagination: Tuple[int, int] = Depends(pagination),
    database: Database = Depends(get_database),
) -> List[PostDB]:
    skip, limit = pagination
    rows = await database.fetch_all(
        posts
        .select()
        .offset(skip)
        .limit(limit)
    )
    results = [PostDB(**row) for row in rows]
    return results


@app.get("/posts/{id}", response_model=PostPublic)
async def get_post(post: PostPublic = Depends(get_post_or_404)) -> PostPublic:
    return post


@app.post(
    "/posts", 
    response_model=PostPublic, 
    status_code=status.HTTP_201_CREATED
)
async def create_post(
    post: PostCreate, 
    database: Database = Depends(get_database)
) -> PostPublic:
    new_post_id = await database.execute(
        posts
        .insert()
        .values(post.dict())
    )
    post_db = await get_post_or_404(new_post_id, database)
    return post_db


@app.patch("/posts/{id}", response_model=PostPublic)
async def update_post(
    post_update: PostPartialUpdate,
    post: PostPublic = Depends(get_post_or_404),
    database: Database = Depends(get_database),
) -> PostPublic:
    new_post_id = await database.execute(
        posts
        .update()
        .where(posts.c.id == post.id)
        .values(post_update.dict(exclude_unset=True))
    )
    post_db = await get_post_or_404(new_post_id, database)
    return post_db


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post: PostPublic = Depends(get_post_or_404),
    database: Database = Depends(get_database),
):
    await database.execute(
        posts
        .delete()
        .where(posts.c.id == post.id)
    )


@app.post(
    "/comments", 
    response_model=CommentDB, 
    status_code=status.HTTP_201_CREATED
)
async def create_comment(
    comment: CommentCreate, 
    database: Database = Depends(get_database)
) -> CommentDB:
    raw_post = await database.fetch_one(
        posts
        .select()
        .where(posts.c.id == comment.post_id)
    )
    if raw_post is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Post {id} does not exist"
        )

    new_comment_id = await database.execute(
        comments
        .insert()
        .values(comment.dict())
    )    
    raw_comment = cast(Mapping, await database.fetch_one(
        comments
        .select()
        .where(comments.c.id == new_comment_id)
    ))

    return CommentDB(**raw_comment)
