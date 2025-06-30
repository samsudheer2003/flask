import unittest
import json
from app import create_app
from config import TestConfig
from models import db, User

class TodoRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

            
            self.client.post('/user/register', data=json.dumps({
                "username": "testuser",
                "first_name": "Test",
                "last_name": "User",
                "email": "testuser@example.com",
                "mobile_number": "1234567890",
                "password": "TestPass123"
            }), content_type='application/json')

            
            login_res = self.client.post('/user/login', data=json.dumps({
                "username": "testuser",
                "password": "TestPass123"
            }), content_type='application/json')
            
            self.access_token = login_res.get_json()['access_token']
            self.auth_header = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }

            self.user_uid = User.query.filter_by(username="testuser").first().uid



    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_todo_success(self):
        data = {
            "task": "Test Todo Task",
            "status": "pending"
        }
        response = self.client.post(
            '/todo/',
            data=json.dumps(data),
            headers=self.auth_header  
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn('Todo created successfully', response.get_json().get('message'))


    def test_create_todo_invalid_status(self):
        data = {
            "task": "Test Task",
            "status": "invalid_status"
        }
        response = self.client.post(
            '/todo/',
            data=json.dumps(data),
            headers=self.auth_header  
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid status value', str(response.get_json()))


    def test_get_todos_success(self):
        self.client.post('/todo/', data=json.dumps({
            "task": "Fetch me",
            "status": "pending"
        }), headers=self.auth_header)

        response = self.client.get('/todo/', headers=self.auth_header)  
        self.assertEqual(response.status_code, 200)
        self.assertIn('todos', response.get_json())


    def test_update_todo(self):
        res = self.client.post('/todo/', data=json.dumps({
            "task": "To update",
            "status": "pending"
        }), headers=self.auth_header)

        self.assertEqual(res.status_code, 201)
        todo_uid = res.get_json()['todo']['uid']

        update_data = {
            "task": "Updated Task",
            "status": "completed"
        }
        response = self.client.put(
            f'/todo/update?todo_uid={todo_uid}',
            data=json.dumps(update_data),
            headers=self.auth_header 
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('Todo updated successfully', response.get_json()['message'])


    def test_delete_todo(self):
        res = self.client.post('/todo/', data=json.dumps({
            "task": "To delete",
            "status": "pending"
        }), headers=self.auth_header)

        self.assertEqual(res.status_code, 201)
        todo_uid = res.get_json()['todo']['uid']

        response = self.client.delete(
            f'/todo/delete?todo_id={todo_uid}',
            headers=self.auth_header  
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('Todo deleted successfully', response.get_json()['message'])
