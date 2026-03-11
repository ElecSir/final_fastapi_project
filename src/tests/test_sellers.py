import pytest
from fastapi import status
from icecream import ic
from sqlalchemy import select

from src.models.books import Book
from src.models.sellers import Seller

API_V1_URL_PREFIX = "/api/v1/sellers"


# Тест на создание продавца
@pytest.mark.asyncio()
async def test_create_seller(async_client):
    data = {
        "first_name": "John",
        "last_name": "James",
        "e_mail": "john@example.com",
        "password": "pass12345678",
    }
    response = await async_client.post(f"{API_V1_URL_PREFIX}/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    resp_seller_id = result_data.pop("id", None)
    assert resp_seller_id is not None, "Seller id not returned from endpoint"

    assert result_data == {
        "first_name": "John",
        "last_name": "James",
        "e_mail": "john@example.com",
    }

    # Проверяем, что пароль не возвращается
    assert "password" not in result_data


# Тест на валидацию email
@pytest.mark.asyncio()
async def test_create_seller_with_invalid_email(async_client):
    data = {
        "first_name": "John",
        "last_name": "James",
        "e_mail": "invalid-email",
        "password": "pass12345678",
    }
    response = await async_client.post(f"{API_V1_URL_PREFIX}/", json=data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# Тест на валидацию пароля
@pytest.mark.asyncio()
async def test_create_seller_with_short_password(async_client):
    data = {
        "first_name": "John",
        "last_name": "James",
        "e_mail": "john@example.com",
        "password": "short",
    }
    response = await async_client.post(f"{API_V1_URL_PREFIX}/", json=data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# Тест на получение списка продавцов
@pytest.mark.asyncio()
async def test_get_sellers(db_session, async_client):
    seller_1 = Seller(first_name="John", last_name="James", e_mail="john@example.com", password="pass12345678")
    seller_2 = Seller(first_name="Jane", last_name="Smith", e_mail="jane@example.com", password="pass12345678")

    db_session.add_all([seller_1, seller_2])
    await db_session.flush()

    response = await async_client.get(f"{API_V1_URL_PREFIX}/")

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["sellers"]) == 2

    assert response.json() == {
        "sellers": [
            {
                "first_name": "John",
                "last_name": "James",
                "e_mail": "john@example.com",
                "id": seller_1.id,
            },
            {
                "first_name": "Jane",
                "last_name": "Smith",
                "e_mail": "jane@example.com",
                "id": seller_2.id,
            },
        ]
    }

    # Проверяем, что пароли не возвращаются
    for seller_data in response.json()["sellers"]:
        assert "password" not in seller_data


# Тест на получение одного продавца с книгами
@pytest.mark.asyncio()
async def test_get_single_seller(db_session, async_client):
    seller = Seller(first_name="John", last_name="James", e_mail="john@example.com", password="pass12345678")
    db_session.add(seller)
    await db_session.flush()

    book = Book(title="Clean Code", author="Robert Martin", year=2022, pages=22, seller_id=seller.id)
    db_session.add(book)
    await db_session.flush()

    response = await async_client.get(f"{API_V1_URL_PREFIX}/{seller.id}")

    assert response.status_code == status.HTTP_200_OK

    result_data = response.json()

    assert result_data == {
        "first_name": "John",
        "last_name": "James",
        "e_mail": "john@example.com",
        "id": seller.id,
        "books": [
            {
                "title": "Clean Code",
                "author": "Robert Martin",
                "year": 2022,
                "pages": 22,
                "id": book.id,
                "seller_id": seller.id,
            }
        ]
    }

    assert "password" not in result_data


# Тест на получение несуществующего продавца
@pytest.mark.asyncio()
async def test_get_single_seller_with_wrong_id(db_session, async_client):
    seller = Seller(first_name="John", last_name="James", e_mail="john@example.com", password="pass12345678")
    db_session.add(seller)
    await db_session.flush()

    response = await async_client.get(f"{API_V1_URL_PREFIX}/{seller.id + 1}")

    assert response.status_code == status.HTTP_404_NOT_FOUND


# Тест на обновление продавца
@pytest.mark.asyncio()
async def test_update_seller(db_session, async_client):
    seller = Seller(first_name="John", last_name="James", e_mail="john@example.com", password="pass12345678")
    db_session.add(seller)
    await db_session.flush()

    data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "e_mail": "jane@example.com",
        "password": "newpass12345678",
        "id": seller.id,
    }

    response = await async_client.put(f"{API_V1_URL_PREFIX}/{seller.id}", json=data)

    print(f"Response: {response.json()}")

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что данные обновились
    res = await db_session.get(Seller, seller.id)
    assert res.first_name == "Jane"
    assert res.last_name == "Smith"
    assert res.e_mail == "jane@example.com"
    assert res.password == "pass12345678" # Пароль не обновился
    assert res.id == seller.id


# Тест на удаление продавца
@pytest.mark.asyncio()
async def test_delete_seller(db_session, async_client):
    seller = Seller(first_name="John", last_name="James", e_mail="john@example.com", password="pass12345678")

    db_session.add(seller)
    await db_session.flush()
    ic(seller.id)

    response = await async_client.delete(f"{API_V1_URL_PREFIX}/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    await db_session.flush()
    all_sellers = await db_session.execute(select(Seller))
    res = all_sellers.scalars().all()

    assert len(res) == 0


# Тест на удаление несуществующего продавца
@pytest.mark.asyncio()
async def test_delete_seller_with_invalid_seller_id(db_session, async_client):
    seller = Seller(first_name="John", last_name="James", e_mail="john@example.com", password="pass12345678")

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.delete(f"{API_V1_URL_PREFIX}/{seller.id + 1}")

    assert response.status_code == status.HTTP_404_NOT_FOUND


# Тест на удаление книг при удалении продавца
@pytest.mark.asyncio()
async def test_delete_seller_with_books(db_session, async_client):
    seller = Seller(first_name="John", last_name="James", e_mail="john@example.com", password="pass12345678")
    db_session.add(seller)
    await db_session.flush()

    book = Book(title="Clean Code", author="Robert Martin", year=2022, pages=22, seller_id=seller.id)
    db_session.add(book)
    await db_session.flush()

    response = await async_client.delete(f"{API_V1_URL_PREFIX}/{seller.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    await db_session.flush()

    # Проверяем, что книга тоже удалена
    all_books = await db_session.execute(select(Book))
    res = all_books.scalars().all()
    assert len(res) == 0