from fastapi import Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2
from sqlalchemy.orm import Session
from .. database import get_db
from typing import List, Optional

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

# Get All Posts
@router.get("/", response_model=List[schemas.Post])
def get_posts(db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user), limit: int = 5, skip: int = 0, search: Optional[str] = ""):
    # Pagination can be implemented by using limit and skip/offest together
    # e.g. limit of 5 shows the first 5 results on a page then on click of next pg button you can query to skip the existing 5 and show the next 5 results 
    posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts

# Create Post
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    # new_post = models.Post(title=post.title, content=post.content, published=post.published)
    new_post = models.Post(owner_id=current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return  new_post


# Get Post with id
@router.get("/{id}", response_model=schemas.Post)
def get_post(id: int, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} not found")
    return post


# Delete Post with id
@router.delete("/{id}")
def delete_post(id: int, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Update Post with id
@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    post_query.update(updated_post.model_dump(), synchronize_session=False)
    db.commit()
    return post_query.first()