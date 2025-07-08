# YayTravel FastAPI Backend

This is a lightweight FastAPI backend for the YayTravel web application. It provides user authentication using JWT tokens and user management with a MongoDB database.

## Features

-   **FastAPI Framework**: Modern, fast (high-performance), web framework for building APIs.
-   **MongoDB Integration**: Uses `motor` for asynchronous database operations with MongoDB.
-   **JWT Authentication**: Secure endpoints using JSON Web Tokens.
-   **Password Hashing**: User passwords are securely hashed using `passlib`.
-   **Docker & Cloud Run**: Ready for containerization and deployment on Google Cloud Run.
-   **Comprehensive Testing**: Unit and integration tests using `pytest`.

---

## 1. Project Setup

Follow these steps to get the backend running on your local machine.

### Prerequisites

-   Python 3.7+
-   A running MongoDB instance. You can [install it locally](https://www.mongodb.com/try/download/community) or use a cloud service like MongoDB Atlas.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd yaytravel-backend
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    # On Windows, use: venv\Scripts\activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Create a file named `.env` in the project root. This file holds your configuration and secrets. **It should never be committed to version control.**

    Copy the following into your `.env` file and replace the placeholder values:

    ```env
    # Your actual MongoDB connection string
    MONGODB_URL="mongodb://localhost:27017" 
    
    # A long, random, and secret string for signing JWTs
    SECRET_KEY="your-super-secret-key-that-is-very-long-and-random" 
    
    # The algorithm used to sign the JWT
    ALGORITHM="HS256" 
    
    # How long an access token is valid (in minutes)
    ACCESS_TOKEN_EXPIRE_MINUTES=30 
    ```

---

## 2. Running the Application

With the setup complete, you can start the web server:

```bash
uvicorn main:app --reload
```

-   `--reload`: This flag enables auto-reloading, so the server will restart automatically after you make changes to the code.

The application will be running at `http://127.0.0.1:8000`.

### Interactive API Documentation

FastAPI automatically generates interactive documentation for your API. Once the server is running, you can access it at:

-   **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
-   **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

You can use these interfaces to explore and test the API endpoints directly from your browser.

---

## 3. API Endpoints

### Authentication

#### `POST /token`

Authenticates a user and returns a JWT access token.

-   **Request Body**: `application/x-www-form-urlencoded`
    -   `username`: The user's email address.
    -   `password`: The user's plain-text password.
-   **Example Request (`curl`):**
    ```bash
    curl -X POST "http://127.0.0.1:8000/token" \
         -H "Content-Type: application/x-www-form-urlencoded" \
         -d "username=alexchoidev@gmail.com&password=yourpassword"
    ```
-   **Success Response (200 OK):**
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "bearer"
    }
    ```

### Users

#### `POST /users/`

Creates a new user in the database.

-   **Request Body**: `application/json`
-   **Example Request (`curl`):**
    ```bash
    curl -X POST "http://127.0.0.1:8000/users/" \
         -H "Content-Type: application/json" \
         -d '{
               "FirstName": "Alex",
               "LastName": "Choi",
               "email": "alexchoidev@gmail.com",
               "phoneNumber": "+447835588859",
               "password": "a-strong-password"
             }'
    ```
-   **Success Response (201 Created):**
    ```json
    {
        "FirstName": "Alex",
        "LastName": "Choi",
        "email": "alexchoidev@gmail.com",
        "phoneNumber": "+447835588859",
        "id": "686be51b386780da3a6bbdb5"
    }
    ```

#### `GET /users/me`

Retrieves the profile of the currently authenticated user.

-   **Authentication**: Requires a valid JWT token.
-   **Example Request (`curl`):**
    ```bash
    curl -X GET "http://127.0.0.1:8000/users/me" \
         -H "Authorization: Bearer <your_access_token>"
    ```
-   **Success Response (200 OK):**
    ```json
    {
        "FirstName": "Alex",
        "LastName": "Choi",
        "email": "alexchoidev@gmail.com",
        "phoneNumber": "+447835588859",
        "id": "686be51b386780da3a6bbdb5"
    }
    ```

---

## 4. Frontend Integration Guide

Here's how a frontend application can interact with this backend.

### Authentication Flow

1.  **Login**: The user enters their email and password into a login form. The frontend sends these credentials to the `POST /token` endpoint.
2.  **Store Token**: If the credentials are valid, the backend returns an `access_token`. The frontend should store this token securely (e.g., in `localStorage`, `sessionStorage`, or an HttpOnly cookie).
3.  **Authenticated Requests**: For any subsequent request to a protected endpoint (like `GET /users/me`), the frontend must include the stored token in the `Authorization` header. The format is `Bearer <token>`.

### JavaScript `fetch` Examples

#### Creating a New User

```javascript
async function createUser(userData) {
  const response = await fetch('http://127.0.0.1:8000/users/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(userData),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to create user');
  }

  return response.json();
}

// Usage:
const newUser = {
  FirstName: "Jane",
  LastName: "Doe",
  email: "jane.doe@example.com",
  phoneNumber: "+1234567890",
  password: "securepassword123"
};
createUser(newUser).then(user => console.log('User created:', user));
```

#### Logging In to Get a Token

```javascript
async function loginAndGetToken(email, password) {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);

  const response = await fetch('http://127.0.0.1:8000/token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Login failed');
  }

  const tokenData = await response.json();
  // Store the token for future use
  localStorage.setItem('accessToken', tokenData.access_token);
  
  return tokenData;
}

// Usage:
loginAndGetToken('jane.doe@example.com', 'securepassword123')
  .then(data => console.log('Login successful:', data));
```

#### Fetching Authenticated User Profile

```javascript
async function fetchUserProfile() {
  const token = localStorage.getItem('accessToken');
  if (!token) {
    throw new Error('No access token found. Please log in.');
  }

  const response = await fetch('http://127.0.0.1:8000/users/me', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to fetch user profile');
  }

  return response.json();
}

// Usage:
fetchUserProfile().then(profile => console.log('User profile:', profile));
```

---

## 5. Testing

The project uses `pytest` for testing.

1.  **Install development dependencies:**
    ```bash
    pip install -r requirements-dev.txt
    ```

2.  **Prerequisite**: Ensure a local MongoDB instance is running on `localhost:27017`. The tests use a separate database named `test_prosusware` and will not affect your development data.

3.  **Run the tests:**
    ```bash
    python -m pytest
    ```

---

## 6. Deployment to Google Cloud Run

This project is configured for easy deployment using Docker and Google Cloud Build.

1.  **Prerequisites**:
    -   Google Cloud SDK (`gcloud`) installed and authenticated.
    -   A Google Cloud project with the **Cloud Build** and **Cloud Run** APIs enabled.
    -   (Recommended) **Secret Manager** API enabled for handling secrets.

2.  **Deployment Command**:
    From the project root, run the following command. It will use the `cloudbuild.yaml` file to build the Docker image, push it to Google Container Registry, and deploy it to Cloud Run.

    ```bash
    gcloud builds submit --config cloudbuild.yaml .
    ```

3.  **Production Secrets**: The `cloudbuild.yaml` file includes a commented-out section for using Google Secret Manager. This is the recommended way to handle your `MONGODB_URL` and `SECRET_KEY` in production. You will need to create the secrets in your GCP project and grant the Cloud Build service account permission to access them. 