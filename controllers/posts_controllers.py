from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
import models
import schemas


# Obtener posts por canal
def get_posts_by_channel(channel_id: int, db: Session):
    posts = db.query(models.Post).filter(models.Post.channel_id == channel_id).all()

    return [
        {
            "post_id": p.post_id,
            "channel_id": p.channel_id,
            "user_id": p.user_id,
            "title": p.title,
            "content": p.content,
            "tags": p.tags,  # ← nuevo campo
            "date": p.date,
        }
        for p in posts
    ]


# Crear un nuevo post
def create_post(post: schemas.PostCreate, user_id: int, db: Session):
    if not db.query(models.User).filter(models.User.user_id == user_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not db.query(models.Channel).filter(models.Channel.channel_id == post.channel_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")

    subscription = (
        db.query(models.Subscription)
        .filter_by(user_id=user_id, channel_id=post.channel_id, is_admin=True)
        .first()
    )

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para publicar en este canal.",
        )

    new_post = models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return JSONResponse(
        content={"msg": "SUCCESS", "post_id": new_post.post_id},
        status_code=status.HTTP_201_CREATED,
    )


def update_post(post_id: int, user_id: int, post_data: schemas.PostUpdate, db: Session):
    post = db.query(models.Post).filter(models.Post.post_id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    subscription = (
        db.query(models.Subscription)
        .filter_by(user_id=user_id, channel_id=post.channel_id, is_admin=True)
        .first()
    )
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para editar en este canal.",
        )

    if post_data.title is not None:
        post.title = post_data.title
    if post_data.content is not None:
        post.content = post_data.content
    if post_data.tags is not None:
        post.tags = post_data.tags

    db.commit()
    db.refresh(post)

    return JSONResponse(
        content={"msg": "SUCCESS", "post_id": post.post_id},
        status_code=status.HTTP_200_OK,
    )


def delete_post(post_id: int, user_id: int, db: Session):
    post = db.query(models.Post).filter(models.Post.post_id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    subscription = (
        db.query(models.Subscription)
        .filter_by(user_id=user_id, channel_id=post.channel_id, is_admin=True)
        .first()
    )
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar en este canal.",
        )

    db.delete(post)
    db.commit()

    return JSONResponse(
        content={"msg": "SUCCESS"},
        status_code=status.HTTP_200_OK,
    )


def get_recent_user_posts(user_id: int, db: Session):
    # Subconsulta que filtra solo canales favoritos
    subscribed_channel_ids = (
        db.query(models.Subscription.channel_id)
        .filter(
            models.Subscription.user_id == user_id,
            models.Subscription.is_subscribed == True,  # ← solo suscritos
        )
        .subquery()
    )

    # Consulta de los posts recientes de esos canales
    recent_posts = (
        db.query(
            models.Post.post_id,
            models.Post.channel_id,
            models.Post.user_id,
            models.Post.title,
            models.Post.content,
            models.Post.tags,
            models.Post.date,
            models.Channel.channel_name,
        )
        .join(models.Channel, models.Post.channel_id == models.Channel.channel_id)
        .filter(models.Post.channel_id.in_(subscribed_channel_ids))
        .order_by(desc(models.Post.date))
        .limit(3)
        .all()
    )

    return [
        {
            "post_id": p.post_id,
            "channel_id": p.channel_id,
            "channel_name": p.channel_name,
            "user_id": p.user_id,
            "title": p.title,
            "content": p.content,
            "tags": p.tags,
            "date": p.date,
        }
        for p in recent_posts
    ]
