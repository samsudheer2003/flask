import unittest
import json
from app import create_app
from config import TestConfig
from models import db, User

class UserRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def register_user(self, user_data):
        return self.client.post(
            '/user/register', 
            data=json.dumps(user_data),
            content_type='application/json'
        )

    def login_user(self, login_data):
        return self.client.post(
            '/user/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )

    def test_register_success(self):
        user_data = {
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "email": "testuser@example.com",
            "mobile_number": "1234567890",
            "password": "Secure123"
        }
        response = self.register_user(user_data)
        self.assertEqual(response.status_code, 201)
        self.assertIn("Registered successfully", response.get_json().get("message"))

    def test_register_duplicate(self):
        user_data = {
            "username": "duplicateuser",
            "first_name": "Test",
            "last_name": "User",
            "email": "duplicate@example.com",
            "mobile_number": "1234567890",
            "password": "Secure123"
        }
        self.register_user(user_data)
        response = self.register_user(user_data)
        self.assertEqual(response.status_code, 409)
        self.assertIn("User already exists", response.get_json().get("message"))

    def test_register_validation_error(self):
        user_data = {
            "username": "t1",
            "first_name": "Test",
            "last_name": "User",
            "email": "not-an-email",
            "mobile_number": "123",
            "password": "abc"
        }
        response = self.register_user(user_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("errors", response.get_json())

    def test_password_strength_validation(self):
        user_data = {
            "username": "weakpass",
            "first_name": "Weak",
            "last_name": "Password",
            "email": "weakpass@example.com",
            "mobile_number": "9876543210",
            "password": "weakpass"
        }
        response = self.register_user(user_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Password must contain at least one uppercase letter", str(response.get_json()))

    def test_login_success(self):
        user_data = {
            "username": "loginuser",
            "first_name": "Login",
            "last_name": "User",
            "email": "loginuser@example.com",
            "mobile_number": "1234567890",
            "password": "Login123"
        }
        self.register_user(user_data)
        response = self.login_user({"username": "loginuser", "password": "Login123"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Login successful", response.get_json().get("message"))

    def test_login_invalid_credentials(self):
        response = self.login_user({"username": "unknown", "password": "invalid"})
        self.assertEqual(response.status_code, 401)
        self.assertIn("Invalid username/email or password", response.get_json().get("message"))

if __name__ == '__main__':
    unittest.main()
