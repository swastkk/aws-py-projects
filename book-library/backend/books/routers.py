import os
import uuid
from typing import List

import boto3
from dotenv import load_dotenv
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

import books.utils as utils
from books.models import BookGET, BookOut
from books.schema import BookCreate
from db import get_db

load_dotenv()


book_router = APIRouter(prefix="/books", tags=["Books"])


@book_router.get("/", response_model=List[BookOut])
def get_books(db: Session = Depends(get_db)):
    return db.execute(text("SELECT * FROM books")).fetchall()


@book_router.post("/add", response_model=BookOut)
def post_book(payload: BookCreate, db: Session = Depends(get_db)):
    book = (
        db.execute(
            text(
                """
            INSERT INTO books (id, name, author, price, image)
            VALUES (:id, :name, :author, :price, :image)
            RETURNING id, name, author, price, image
        """
            ),
            {
                "id": uuid.uuid4(),
                "name": payload.name,
                "author": payload.author,
                "price": payload.price,
                "image": payload.image,
            },
        )
        .mappings()
        .fetchone()
    )
    db.commit()
    return book


@book_router.get("/{book_id}")
def get_book_by_id(book_id: uuid.UUID, db: Session = Depends(get_db)):
    book = dict(
        db.execute(text("SELECT * FROM books WHERE id = :id"), {"id": book_id})
        .mappings()
        .fetchone()
    )
    print(book["image"])
    s3_client = boto3.client(
        "s3",
        region_name="ap-south-1",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )
    book["image_url"] = utils.generate_get_presigned_url(
        s3_client, os.getenv("BUCKET_NAME"), book["image"]
    )
    print(book)
    if not book:
        return JSONResponse(status_code=404, content={"detail": "Book not found"})
    return book


@book_router.delete("/{book_id}")
def delete_book(book_id: uuid.UUID, db: Session = Depends(get_db)):
    result = db.execute(
        text("DELETE FROM books WHERE id = :id RETURNING id"), {"id": book_id}
    )
    deleted_book = result.mappings().fetchone()
    if not deleted_book:
        return JSONResponse(status_code=404, content={"detail": "Book not found"})
    db.commit()
    return {"message": "Book deleted successfully"}


@book_router.put("/{book_id}", response_model=BookOut)
def update_book(book_id: uuid.UUID, payload: BookCreate, db: Session = Depends(get_db)):

    old = (
        db.execute(
            text("SELECT id, name, author, price, image FROM books WHERE id = :id"),
            {"id": book_id},
        )
        .mappings()
        .fetchone()
    )

    if not old:
        return JSONResponse(status_code=404, content={"detail": "Book not found"})

    updated = (
        db.execute(
            text(
                """
            UPDATE books
            SET name = :name,
                author = :author,
                price = :price,
                image = :image
            WHERE id = :id
            RETURNING id, name, author, price, image
        """
            ),
            {
                "id": book_id,
                "name": payload.name if payload.name is not None else old["name"],
                "author": (
                    payload.author if payload.author is not None else old["author"]
                ),
                "price": payload.price if payload.price is not None else old["price"],
                "image": payload.image if payload.image is not None else old["image"],
            },
        )
        .mappings()
        .fetchone()
    )

    db.commit()
    return updated


@book_router.get("/{book_id}/upload")
def upload_book_image(book_id: uuid.UUID, db: Session = Depends(get_db)):
    book = (
        db.execute(text("SELECT * FROM books WHERE id = :id"), {"id": book_id})
        .mappings()
        .fetchone()
    )
    if not book:
        return JSONResponse(status_code=404, content={"detail": "Book not found"})
    try:
        boto3_client = boto3.client(
            "s3",
            region_name="ap-south-1",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
        bucket_name = os.getenv("BUCKET_NAME")
        image_key = utils.generate_image_key(book["name"])
        upload_image_url = utils.generate_put_presigned_url(
            boto3_client, bucket_name, image_key
        )
        response_book_data = dict(book)
        response_book_data["upload_image_url"] = upload_image_url
        response_book_data["image"] = image_key
        # save this key in th db
        db.execute(
            text("UPDATE books SET image = :image WHERE id = :id"),
            {"image": image_key, "id": book_id},
        )
        db.commit()
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"detail": "Error generating upload URL"}
        )

    return response_book_data
