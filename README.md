# Smart Eco-Fleet & Carbon Tracker

A modern, full-stack web application for real-time fleet vehicle management, trip logging, and automated carbon footprint analytics. Designed using **Clean Architecture** principles, **SOLID design patterns**, and a high-performance **FastAPI** backend with a responsive vanilla **HTML5/CSS3/JS** frontend.

---

## 🌟 Core Features

- 🚗 **Vehicle Management**: Register and organize vehicles across diverse power types (Electric Vehicles (EV), Diesel, Petrol, and Hybrid).
- 🛣️ **Trip Logging**: Track individual trips with distance traveled (km), fuel consumed (L), timestamping, and automatic vehicle association.
- 🌿 **Carbon Footprint Engine**: Automated calculation of carbon emissions ($kg\ CO_2$) based on vehicle-specific emission factors:
  - **Diesel**: ~2.68 kg CO₂ / L
  - **Petrol**: ~2.31 kg CO₂ / L
  - **Hybrid**: ~1.50 kg CO₂ / L
  - **EV (Electric)**: 0.00 kg CO₂ / L
- 📊 **Real-Time Analytics Dashboard**: Live updating statistics cards displaying total fleet carbon footprint ($kg\ CO_2$), registered vehicle count, total distance traveled, and trip logs.

---

## 🏗️ Architecture & Tech Stack

### Tech Stack

- **Backend**: Python 3.10+, FastAPI, Pydantic v2, SQLAlchemy 2.0
- **Database**: PostgreSQL (Production) / SQLite (Development)
- **Frontend**: Vanilla JavaScript (ES6+), HTML5, Custom CSS3 Design System (Glassmorphism, CSS Variables, Dark Mode Aesthetics)
- **Server**: Uvicorn ASGI Server

### Clean Architecture Layers

The codebase adheres strictly to Clean Architecture, decoupling core domain business logic from infrastructure and interface frameworks:

```text
app/
├── core/             # Application configuration and DB setup
│   ├── config.py     # Environment variables and settings
│   └── database.py   # SQLAlchemy engine and session factory
├── domain/           # Enterprise domain models & database schemas
│   └── models.py     # Vehicle and TripLog ORM entities
├── use_cases/        # Business logic & carbon calculation engine
│   └── fleet_services.py # Service orchestration and emission logic
├── infrastructure/   # Data access layer & repository implementations
│   └── repositories.py   # SQL query execution & aggregates (func.sum)
└── interfaces/       # API layer & HTTP delivery mechanisms
    └── controllers.py    # FastAPI routes and Pydantic schemas
```

---

## 🧩 OOP & SOLID Principles Mapping

The system was designed with clean software engineering paradigms:

### 1. SOLID Principles
- **Single Responsibility Principle (SRP)**:
  - `controllers.py` handles HTTP request routing and payload validation.
  - `fleet_services.py` executes business rules and carbon calculations.
  - `repositories.py` encapsulates SQL queries and persistence operations.
- **Open/Closed Principle (OCP)**:
  - The carbon emission engine `calculate_carbon_emissions()` is designed to be easily extensible with new vehicle fuel types without modifying existing trip logging pipelines.
- **Liskov Substitution Principle (LSP)**:
  - Domain models (`Vehicle`, `TripLog`) inherit from SQLAlchemy `Base` while upholding consistent attribute interfaces.
- **Interface Segregation Principle (ISP)**:
  - Focused Pydantic schemas (`VehicleCreate`, `VehicleResponse`, `TripCreate`, `TripResponse`, `EmissionsSummaryResponse`) ensure clients only consume data fields relevant to their context.
- **Dependency Inversion Principle (DIP)**:
  - Route handlers depend on database abstractions using FastAPI's dependency injection (`db: Session = Depends(get_db)`).

### 2. Design Patterns
- **Repository Pattern**: `VehicleRepository` and `TripLogRepository` encapsulate data storage mechanisms, isolating domain logic from direct database engine dependencies.
- **Service Pattern**: `FleetService` orchestrates complex business workflows across multiple repositories and calculation engines.

---

## 🚀 How to Run Locally

### Prerequisites

- Python 3.10 or higher
- `pip` package manager

### Setup Steps

1. **Clone the repository / navigate to project directory**:
   ```bash
   cd /path/to/eco_fleet_system
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration (Optional)**:
   Create or verify a `.env` file in the root directory:
   ```env
   PROJECT_TITLE="Smart Eco-Fleet & Carbon Tracker"
   PROJECT_VERSION="1.0.0"
   DATABASE_URL="sqlite:///./eco_fleet.db"
   ```

5. **Start the Uvicorn server**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

6. **Access the Application**:
   - 🌐 **Interactive Dashboard**: [http://localhost:8000](http://localhost:8000)
   - 📚 **Swagger API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - 📖 **ReDoc API Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
