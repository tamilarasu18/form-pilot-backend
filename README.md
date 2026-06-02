# Farm Pilot API

Farm Pilot API is the backend service powering the Farm Pilot application. Built with FastAPI and SQLAlchemy, it provides a robust, high-performance RESTful API for managing agricultural data, including users, lands, sections, crops, daily logs, and expenses.

## 🌟 Features

- **Authentication & Authorization**: Secure JWT-based authentication system.
- **Entity Management**: Full CRUD operations for Lands, Sections, and Crops.
- **Comprehensive Logging**: Track daily farming activities, weather conditions, crop health, and related expenses.
- **Asynchronous Operations**: Fully asynchronous database interactions for high performance and scalability.

## 🚀 Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Language**: Python 3.10+
- **Database**: SQLite (via `aiosqlite`)
- **ORM**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (Async)
- **Data Validation**: [Pydantic V2](https://docs.pydantic.dev/latest/)
- **Authentication**: `python-jose`, `passlib`

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd farm-pilot-backend
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Unix/macOS
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Environment Variables**:
   Create a `.env` file in the root directory and add the following:
   ```env
   SECRET_KEY=your_secret_key_here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=1440
   DATABASE_URL=sqlite+aiosqlite:///./farmpilot.db
   ```

## 🛠️ Running the API

To start the local development server with live reload:
```bash
uvicorn main:app --reload
```
The API will be accessible at [http://localhost:8000](http://localhost:8000).

- **Interactive API Documentation (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative API Documentation (ReDoc)**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 📄 License

This project is licensed under the MIT License.
