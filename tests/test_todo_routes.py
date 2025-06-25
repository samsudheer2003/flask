import unittest
import json
from app import app
from models import db, User

class TodoRoutesTestCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        self.client = app.test_client()
        with app.app_context():
            db.create_all()

            response = self.client.post('/register', data=json.dumps({
                "username": "testuser",
                "first_name": "Test",
                "last_name": "User",
                "email": "testuser@example.com",
                "mobile_number": "1234567890",
                "password": "TestPass123"
            }), content_type='application/json')
            self.assertEqual(response.status_code, 201)
            self.user_uid = User.query.filter_by(username="testuser").first().uid

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_todo_success(self):
        data = {
            "task": "Test Todo Task",
            "status": "pending"
        }
        response = self.client.post(f'/todo?user_id={self.user_uid}', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('Todo created successfully', response.get_json().get('message'))

    def test_create_todo_invalid_status(self):
        data = {
            "task": "Test Task",
            "status": "invalid_status"
        }
        response = self.client.post(f'/todo?user_id={self.user_uid}', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid status value', str(response.get_json()))

    def test_get_todos_success(self):
        self.client.post(f'/todo?user_id={self.user_uid}', data=json.dumps({
            "task": "Fetch me",
            "status": "pending"
        }), content_type='application/json')

        response = self.client.get(f'/todo?user_id={self.user_uid}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('todos', response.get_json())

    def test_update_todo(self):
        res = self.client.post(f'/todo?user_id={self.user_uid}', data=json.dumps({
            "task": "To update",
            "status": "pending"
        }), content_type='application/json')

        self.assertEqual(res.status_code, 201)
        todo_id = res.get_json()['todo']['id']

        update_data = {
            "task": "Updated Task",
            "status": "completed"
        }
        response = self.client.put(
            f'/todo/{todo_id}',
            data=json.dumps(update_data),
            headers={"User-Id": self.user_uid},
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('Todo updated successfully', response.get_json()['message'])

    def test_delete_todo(self):
        res = self.client.post(f'/todo?user_id={self.user_uid}', data=json.dumps({
            "task": "To delete",
            "status": "pending"
        }), content_type='application/json')

        self.assertEqual(res.status_code, 201)
        todo_uid = res.get_json()['todo']['uid']

        response = self.client.delete(
            f'/todo/delete?user_id={self.user_uid}&todo_id={todo_uid}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('Todo deleted successfully', response.get_json()['message'])

if __name__ == '__main__':
    unittest.main()
