from fastapi import FastAPI, HTTPException, status
from chapter4_models import (
    PostPublic, PostCreate, PostDB, PostPartialUpdate, DummyDatabase
)


db = DummyDatabase()
app = FastAPI()


@app.post(
    "/posts", 
    status_code=status.HTTP_201_CREATED, 
    response_model=PostPublic
)
async def create(post_create: PostCreate):
    new_id = max(db.posts.keys() or (0,)) + 1
    post = PostDB(id=new_id, **post_create.dict())
    db.posts[new_id] = post
    return post


@app.patch("/posts/{id}", response_model=PostPublic)
async def partial_update(id: int, post_update: PostPartialUpdate):
    
    # Insert test data to the dummy db
    db.posts.update({2: PostDB(id=2, title='mytitle1', content='mycontent1')})
    
    try:
        post_db = db.posts[id]
        
        # Only the fields that the user sent in the payload are created
        updated_fields = post_update.dict(exclude_unset=True) 
        
        # 'update' expects a dict with the fields that should be updated during the copy
        updated_post = post_db.copy(update=updated_fields) 
        
        db.posts[id] = updated_post
        return updated_post
    
    except KeyError:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
