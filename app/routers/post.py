from operator import mod
from os import curdir

from sqlalchemy import func
from .. import models, schemas, oauth2
from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db


router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)

def getPosts(db, search: Optional[str] = ""):
    posts = db.query(models.Post, func.count(models.Like.post_id).label("likes")).join(models.Like, models.Like.post_id==models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search))
    return posts

@router.get("/", response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db),limit: int = 10,skip: int = 0,search: Optional[str] = ""):
    # cursor.execute("""SELECT * FROM posts;""")
    # posts = cursor.fetchall()
    
    posts = getPosts(db, search).offset(skip).limit(limit).all()
    return posts

@router.get("/user",response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user),limit: int = 10,skip: int = 0,search: Optional[str] = ""):
    # cursor.execute("""SELECT * FROM posts;""")
    # posts = cursor.fetchall()
    posts = getPosts(db, search).filter(models.Post.owner_id==current_user.id).offset(skip).limit(limit).all()
    return posts

@router.get("/{id}",response_model=schemas.PostOut)
def get_posts(id: int,db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts WHERE id = %s """,(str(id)))
    # post = cursor.fetchone()
    post = getPosts(db).filter(models.Post.id == id).first()
    if(not post):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="post not found!")
    return post

@router.post("/",status_code=status.HTTP_201_CREATED,response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """,(post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    new_post=models.Post(owner_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING * """,(str(id)))
    # post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if(post == None):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="post not found!")
    if post.owner_id != current_user.id :
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not authorized!")

    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}",response_model=schemas.Post)
def update_post(updt_post: schemas.PostCreate,id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published =%s WHERE id = %s RETURNING * """,(post.title, post.content, post.published,str(id)))
    # updt_post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if(post == None):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="post not found!")
    if post.owner_id != current_user.id :
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not authorized!")
    post_query.update(updt_post.dict(),synchronize_session=False)
    db.commit()
    return post_query.first()