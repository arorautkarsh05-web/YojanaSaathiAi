import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal, Base, engine
from app.models import User

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Uttar Pradesh" in data["geography"]

def test_user_registration_and_login():
    test_email = "ramesh.farmer@example.com"
    # Register
    reg_resp = client.post("/api/v1/auth/register", json={
        "email": test_email,
        "password": "StrongFarmerPassword123!",
        "display_name": "Ramesh Kumar",
        "terms_consented": True
    })
    assert reg_resp.status_code in [201, 400] # 201 on first run, 400 if already exists

    # Login
    login_resp = client.post("/api/v1/auth/login", json={
        "email": test_email,
        "password": "StrongFarmerPassword123!"
    })
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert "access_token" in login_data
    assert login_data["user"]["email"] == test_email
    assert "FARMER" in login_data["user"]["roles"]

def test_generic_login_failure():
    resp = client.post("/api/v1/auth/login", json={
        "email": "nonexistent.farmer@example.com",
        "password": "WrongPassword!"
    })
    assert resp.status_code == 401
    assert "Invalid email or password." in resp.json()["detail"]

def test_guest_workflow_without_account():
    # Discover schemes as guest
    resp = client.post("/api/v1/recommendations", json={
        "stated_needs": ["irrigation", "income_support"],
        "profile": {
            "district": "Ayodhya",
            "landholding_acres": 2.2,
            "farmer_category": "SMALL",
            "primary_crops": ["wheat", "paddy"],
            "irrigation_source": "tubeWell",
            "is_temporary": True
        }
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_schemes_evaluated"] >= 5
    assert len(data["schemes"]) >= 5

def test_unauthorized_admin_endpoint():
    # Calling admin endpoint without token must return 401
    resp = client.get("/api/v1/admin/overview")
    assert resp.status_code == 401

