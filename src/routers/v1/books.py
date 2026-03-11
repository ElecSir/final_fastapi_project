from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.configurations.database import get_async_session
from src.models.sellers import Seller
from src.schemas import IncomingBook, PatchBook, ReturnedAllBooks, ReturnedBook
from src.services import BookService

books_router = APIRouter(prefix="/books", tags=["books"])

DBSession = Annotated[AsyncSession, Depends(get_async_session)]


@books_router.get("/", response_model=ReturnedAllBooks)
async def get_all_books(session: DBSession):
    books = await BookService(session).get_all_books()
    return {"books": books}


@books_router.post("/", response_model=ReturnedBook, status_code=status.HTTP_201_CREATED)
async def create_book(book: IncomingBook, session: DBSession):
    seller = await session.get(Seller, book.seller_id)
    if not seller:
        return Response(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)

    new_book = await BookService(session).add_book(book)
    return new_book


@books_router.get("/{book_id}", response_model=ReturnedBook)
async def get_single_book(book_id: int, session: DBSession):
    book = await BookService(session).get_single_book(book_id)

    if book is not None:
        return book

    return Response(status_code=status.HTTP_404_NOT_FOUND)


@books_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int, session: DBSession):

    deleted_book = await BookService(session).delete_book(book_id)

    if not deleted_book:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@books_router.put("/{book_id}", response_model=ReturnedBook)
async def update_book(book_id: int, new_book_data: ReturnedBook, session: DBSession):

    if new_book_data.seller_id is not None:
        seller = await session.get(Seller, new_book_data.seller_id)
        if not seller:
            return Response(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)

    updated_book = await BookService(session).update_book(book_id, new_book_data)

    if not updated_book:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    return updated_book


@books_router.patch("/{book_id}", response_model=ReturnedBook)
async def patch_book(book_id: int, patched_book: PatchBook, session: DBSession):
    if patched_book.seller_id is not None:
        seller = await session.get(Seller, patched_book.seller_id)
        if not seller:
            return Response(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)

    book = await BookService(session).partial_update_book(book_id, patched_book)

    if not book:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    
    return book

