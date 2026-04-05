import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app, get_db
from database import Base

# Setup Database khusus untuk Testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_tugasfarid.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Reset database setiap test dijalankan agar bersih
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

# Variabel Global untuk menyimpan token
token_admin = ""
token_user = ""

# ==========================================
# 1. TEST ALUR AUTENTIKASI (Harus jalan duluan)
# ==========================================
def test_register_and_login():
    global token_admin, token_user
    
    # Register & Login sebagai ADMIN
    client.post("/register", json={"username": "admin_fariid", "password": "123", "role": "admin"})
    res_admin = client.post("/login", data={"username": "admin_fariid", "password": "123"})
    token_admin = res_admin.json()["access_token"]
    
    # Register & Login sebagai USER BIASA
    client.post("/register", json={"username": "user_biasa", "password": "123", "role": "user"})
    res_user = client.post("/login", data={"username": "user_biasa", "password": "123"})
    token_user = res_user.json()["access_token"]
    
    assert token_admin is not None
    assert token_user is not None

# ==========================================
# 2. TEST CRUD OPERASIONAL
# ==========================================
def test_create_item():
    # Create item butuh login, jadi kita sisipkan token di Headers
    response = client.post(
        "/items/",
        json={"name": "Laptop", "description": "Laptop Asus ROG"},
        headers={"Authorization": f"Bearer {token_admin}"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Laptop"

def test_read_items():
    # Read item bebas diakses tanpa token
    response = client.get("/items/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_read_item():
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Laptop"

def test_update_item():
    response = client.put(
        "/items/1",
        json={"name": "Laptop Update", "description": "Spesifikasi baru"},
        headers={"Authorization": f"Bearer {token_admin}"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Laptop Update"

# ==========================================
# 3. TEST PENGUJIAN RBAC (Access Denied)
# ==========================================
def test_rbac_user_cannot_delete():
    # Coba hapus item pakai token USER BIASA -> Harus gagal / 403 Forbidden
    response = client.delete(
        "/items/1",
        headers={"Authorization": f"Bearer {token_user}"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Access Denied"

def test_delete_item():
    # Hapus item pakai token ADMIN -> Harus sukses
    response = client.delete(
        "/items/1",
        headers={"Authorization": f"Bearer {token_admin}"}
    )
    assert response.status_code == 200