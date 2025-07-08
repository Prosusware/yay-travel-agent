import os
import pytest
import pytest_asyncio
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

# Set the environment for testing BEFORE importing the app
os.environ["MONGODB_URL"] = "mongodb://localhost:27017/test_prosusware"
os.environ["SECRET_KEY"] = "test-secret-key"

from main import app, get_current_user, User


# A fixture to provide a test client for the app
@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture(scope="module")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c


# Fixture to clean up the database after tests
@pytest_asyncio.fixture(scope="module", autouse=True)
async def db_cleanup():
    # Setup: connect and clear db
    client = AsyncIOMotorClient(os.environ["MONGODB_URL"])
    db = client.get_database()
    await db.command("dropDatabase")

    yield

    # Teardown: drop database
    await db.command("dropDatabase")
    client.close()


async def override_get_current_user():
    # This mock user will be "returned" by the dependency override
    return User(
        _id="686be51b386780da3a6bbdb5",
        FirstName="Test",
        LastName="User",
        email="testuser@example.com",
        phoneNumber="+1234567890",
    )


@pytest.mark.asyncio
async def test_read_root(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to YayTravel Backend!"}


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    response = await client.post(
        "/users/",
        json={
            "FirstName": "Test",
            "LastName": "User",
            "email": "test@example.com",
            "phoneNumber": "+1234567890",
            "password": "testpassword",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "password" not in data  # Ensure password is not returned
    assert data["FirstName"] == "Test"


@pytest.mark.asyncio
async def test_create_user_existing_email(client: AsyncClient):
    # First, create a user
    await client.post(
        "/users/",
        json={
            "FirstName": "Jane",
            "LastName": "Doe",
            "email": "jane.doe@example.com",
            "phoneNumber": "+0987654321",
            "password": "password123",
        },
    )

    # Then, try to create another user with the same email
    response = await client.post(
        "/users/",
        json={
            "FirstName": "John",
            "LastName": "Doe",
            "email": "jane.doe@example.com",
            "phoneNumber": "+1122334455",
            "password": "anotherpassword",
        },
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "User with this email already exists"}


@pytest.mark.asyncio
async def test_login_for_access_token(client: AsyncClient):
    # Create user first
    await client.post(
        "/users/",
        json={
            "FirstName": "Login",
            "LastName": "Test",
            "email": "login@test.com",
            "phoneNumber": "+5555555555",
            "password": "goodpassword",
        },
    )

    # Now login
    response = await client.post(
        "/token",
        data={"username": "login@test.com", "password": "goodpassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post(
        "/users/",
        json={
            "FirstName": "Wrong",
            "LastName": "Pass",
            "email": "wrongpass@test.com",
            "phoneNumber": "+4444444444",
            "password": "correctpassword",
        },
    )

    response = await client.post(
        "/token",
        data={"username": "wrongpass@test.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}


@pytest.mark.asyncio
async def test_read_users_me(client: AsyncClient):
    # Override the dependency to mock authentication
    app.dependency_overrides[get_current_user] = override_get_current_user

    response = await client.get(
        "/users/me", headers={"Authorization": "Bearer fake-token"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testuser@example.com"

    # Clean up the override after the test
    app.dependency_overrides = {} 