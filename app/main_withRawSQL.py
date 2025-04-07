from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from . import models
from .database import engine, SessionLocal, get_db
from sqlalchemy.orm import Session

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

class Post(BaseModel):
    title: str
    content: str
    published: bool = True

try:
    conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='postgres',
                            cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    print("Database connection successful")
except Exception as error:
    print("Database connection failed")
    print(f"Error: {error}")

@app.get("/")
def read_root():
    return {"message": "Hello World!"}

# Get All Posts
@app.get("/posts")
def get_posts():
    cursor.execute(""" SELECT * FROM posts""")
    posts = cursor.fetchall()
    print(posts)
    return {"data": posts}

# Without Pydantic
# @app.post("/createposts")
# def create_posts(payload: dict = Body(...)):  
#     print(payload)
#     return {"new_post": f"title: {payload["title"]} content: {payload["content"]}"}


# With Pydantic
# Create Post
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    cursor.execute("""INSERT INTO posts(title, content, published) VALUES(%s, %s, %s)
                   RETURNING *""", (post.title, post.content, post.published))
    new_post  = cursor.fetchone()
    conn.commit()
    return {"data": new_post}

def find_post(id):
    for post in my_posts:
        if post["id"] == id:
            return post

# Get Post with id
@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} not found")
    print(post)
    return {"data": post}

def find_index_post(id: int):
    for index, post in enumerate(my_posts):
        if post["id"] == id:
            return index

# Delete Post with id
@app.delete("/posts/{id}")
def delete_post(id: int):
    # deleting post
    # find index in the array of posts with the required id
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id),))
    deleted_post = cursor.fetchone()
    conn.commit()
    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Update Post with oid
@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", (post.title, post.content, post.published, str(id)))
    updated_post = cursor.fetchone()
    conn.commit()
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    return {"data": updated_post}


@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"data": posts}