from fastapi import Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2
from sqlalchemy.orm import Session
from ..database import get_db

router = APIRouter(
    prefix="/like",
    tags=['Like']
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def like(like: schemas.Like, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id==like.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post {like.post_id} deos not exist!")

    like_query = db.query(models.Like).filter(models.Like.post_id==like.post_id, models.Like.user_id==current_user.id)
    found_like = like_query.first()
    if(like.val==1):
        if found_like:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"user {current_user.id} has already liked the post {like.post_id}")
        new_like = models.Like(post_id=like.post_id, user_id=current_user.id)
        db.add(new_like)
        db.commit()
        return f"you liked the post {like.post_id}"
    else:
        if not found_like:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user {current_user.id} did not liked the post {like.post_id}")
        like_query.delete(synchronize_session=False)
        db.commit()
        return f"you unliked the post {like.post_id}"