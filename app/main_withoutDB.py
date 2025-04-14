from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    # rating: Optional[int] = None

my_posts = [
    { "title": "Title of post", "content": "Content of Post", "id": 1 }
]

@app.get("/")
def read_root():
    return {"Hello": "Worldieee"}

@app.get("/posts")
def get_posts():
    return {"data": my_posts}

# Without Pydantic
# @app.post("/createposts")
# def create_posts(payload: dict = Body(...)):  
#     print(payload)
#     return {"new_post": f"title: {payload["title"]} content: {payload["content"]}"}

# With Pydantic
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    post_dict = post.model_dump()
    post_dict["id"] = randrange(1, 1000000)
    my_posts.append(post_dict)
    print(my_posts)
    return {"data": post_dict}

def find_post(id):
    for post in my_posts:
        if post["id"] == id:
            return post

@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    print(type(id))
    post = find_post(id)
    if not post:
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"message": f"post with id: {id} not found"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} not found")
    return {"data": post}

def find_index_post(id: int):
    for index, post in enumerate(my_posts):
        if post["id"] == id:
            return index

@app.delete("/posts/{id}")
def delete_post(id: int):
    # deleting post
    # find index in the array of posts with the required id
    index = find_index_post(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    index = find_index_post(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    post_dict = post.model_dump()
    post_dict["id"] = id
    my_posts[index] = post_dict
    return {"data": post_dict}
