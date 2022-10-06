"""
 Tests the application API
"""

import base64
import unittest

from app import app, db


def auth_header(username, password):
    """Returns the authorization header."""
    credentials = f'{username}:{password}'
    b64credentials = base64.b64encode(credentials.encode()).decode('utf-8')
    return {'Authorization': f'Basic {b64credentials}'}


class TestBase(unittest.TestCase):
    """Base for all tests."""

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.db = db
        self.db.recreate()

    def tearDown(self):
        pass


class TestUsers(TestBase):
    """Tests for the user endpoints."""

    def test_user_register(self):
        """Tests if is possible to register a new user."""
        send = {
            "name": "Tiago",
            "email": "escola@escola.escola",
            "username": "teste",
            "password": "1234"
        }
        res = self.client.post('/api/user/register/', json=send)
        self.assertEqual(res.status_code, 201)

    def test_correct_credentials(self):
        """Tests if the user logged on with the correct credentials."""
        credentials = auth_header('homer', '1234')
        res = self.client.get('/api/user/', headers=credentials)
        self.assertEqual(res.status_code, 200)

    def test_wrong_credentials(self):
        """Tests if the user logged on with the wrong credentials."""
        credentials = auth_header('no-user', 'no-password')
        res = self.client.get('/api/user/', headers=credentials)
        self.assertEqual(res.status_code, 403)

    def test_update_user(self):
        """Tests updating user information."""
        credentials = auth_header('homer', '1234')
        sent = {"name": "Test",
                "email": "teste@teste.teste",
                "username": "teste",
                "password": "1234"
                }
        res = self.client.put('/api/user/', json=sent, headers=credentials)
        self.assertEqual(res.status_code, 202)


class TestProjects(TestBase):
    """Tests for the project endpoints."""

    def test_project_list(self):
        """Tests getting the list of projects from the user."""
        credentials = auth_header('homer', '1234')
        res = self.client.get('/api/projects/', headers=credentials)
        self.assertEqual(res.status_code, 200)

    def test_add_project(self):
        """Tests adding a valid project to the list."""
        credentials = auth_header('homer', '1234')
        sent = {
            "title": "Teste",
            "creation_date": "2020-06-28",
            "last_updated": "2020-06-29"
        }
        res = self.client.post('/api/projects/', json=sent, headers=credentials)
        self.assertEqual(res.status_code, 201)

    def test_get_project(self):
        """Tests getting a project form the user list."""
        credentials = auth_header('homer', '1234')
        res = self.client.get('/api/projects/2/', headers=credentials)
        self.assertEqual(res.status_code, 200)

    def test_get_wrong_project(self):
        """Tests getting a project from a different user list."""
        credentials = auth_header('bart', '1234')
        res = self.client.get('/api/projects/1/', headers=credentials)
        self.assertEqual(res.status_code, 404)

    def test_update_project(self):
        """Tests updating a valid project from the user list."""
        credentials = auth_header('homer', '1234')
        sent = {
            "title": "Teste",
            "last_updated": "2020-06-30"
        }
        res = self.client.put('/api/projects/1/', json=sent, headers=credentials)
        self.assertEqual(res.status_code, 202)

    def test_update_wrong_project(self):
        """Tests updating a project from a different user list."""
        credentials = auth_header('bart', '1234')
        sent = {
            "title": "Teste",
            "last_updated": "2020-06-30"
        }
        res = self.client.put('/api/projects/1/', json=sent, headers=credentials)
        self.assertEqual(res.status_code, 404)

    def test_delete_project(self):
        """Tests deleting a valid project from the user list."""
        credentials = auth_header('homer', '1234')
        res = self.client.delete('/api/projects/1/', headers=credentials)
        self.assertEqual(res.status_code, 200)

    def test_delete_wrong_project(self):
        """Tests deleting a project from a different user list."""
        credentials = auth_header('bart', '1234')
        res = self.client.delete('/api/projects/1/', headers=credentials)
        self.assertEqual(res.status_code, 404)


class TestTasks(TestBase):
    """Tests for the tasks endpoints."""

    def test_task_list(self):
        """Tests getting the list of tasks from a project."""
        credentials = auth_header('homer', '1234')
        res = self.client.get('/api/projects/1/tasks/', headers=credentials)
        self.assertEqual(res.status_code, 200)

    def test_task_wrong_list(self):
        """Tests getting the list of tasks from a project that the user doesn't have."""
        credentials = auth_header('bart', '1234')
        res = self.client.get('/api/projects/1/tasks/', headers=credentials)
        self.assertEqual(res.status_code, 404)

    def test_add_task(self):
        """Tests adding a valid task to a project."""
        credentials = auth_header('homer', '1234')
        sent = {
            "title": "Teste",
            "creation_date": "2020-06-30",
            "completed": 1
        }
        res = self.client.post('/api/projects/1/tasks/', json=sent, headers=credentials)
        self.assertEqual(res.status_code, 201)

    def test_add_wrong_task(self):
        """Tests adding a task to a project that the user doesn't have."""
        credentials = auth_header('bart', '1234')
        sent = {
            "title": "Teste",
            "creation_date": "2020-06-30",
            "completed": 1
        }
        res = self.client.post('/api/projects/1/tasks/', json=sent, headers=credentials)
        self.assertEqual(res.status_code, 404)

    def test_get_task(self):
        """Tests getting a valid task from a project ."""
        credentials = auth_header('homer', '1234')
        res = self.client.get('/api/projects/1/tasks/1/', headers=credentials)
        self.assertEqual(res.status_code, 200)

    def test_get_wrong_task_first(self):
        """Tests getting a task that the project doesn't have."""
        credentials = auth_header('bart', '1234')
        res = self.client.get('/api/projects/3/tasks/4/', headers=credentials)
        self.assertEqual(res.status_code, 404)

    def test_get_wrong_task_second(self):
        """Tests getting a task from a project that the user doesn't have."""
        credentials = auth_header('bart', '1234')
        res = self.client.get('/api/projects/1/tasks/1/', headers=credentials)
        self.assertEqual(res.status_code, 404)

    def test_update_task(self):
        """Tests updating a valid task from a project."""
        credentials = auth_header('bart', '1234')
        sent = {
            "title": "Teste",
            "completed": 0
        }
        res = self.client.put('/api/projects/3/tasks/6/', json=sent, headers=credentials)
        self.assertEqual(res.status_code, 202)

    def test_update_wrong_task_first(self):
        """Tests updating a task that the project doesn't have."""
        credentials = auth_header('bart', '1234')
        sent = {
            "title": "Teste",
            "completed": 1
        }
        res = self.client.put('/api/projects/3/tasks/4/', json=sent, headers=credentials)
        self.assertEqual(res.status_code, 404)

    def test_update_wrong_task_second(self):
        """Tests updating a task from a project that the user doesn't have."""
        credentials = auth_header('homer', '1234')
        sent = {
            "title": "Teste",
            "completed": 1
        }
        res = self.client.put('/api/projects/3/tasks/4/', json=sent, headers=credentials)
        self.assertEqual(res.status_code, 404)

    def test_delete_task(self):
        """Tests deleting a valid task from a project."""
        credentials = auth_header('bart', '1234')
        res = self.client.delete('/api/projects/3/tasks/6/', headers=credentials)
        self.assertEqual(res.status_code, 200)

    def test_delete_wrong_task_first(self):
        """Tests deleting a task that the project doesn't have."""
        credentials = auth_header('bart', '1234')
        res = self.client.delete('/api/projects/3/tasks/4/', headers=credentials)
        self.assertEqual(res.status_code, 404)

    def test_delete_wrong_task_second(self):
        """Tests deleting a task from a project that the user doesn't have."""
        credentials = auth_header('bart', '1234')
        res = self.client.delete('/api/projects/1/tasks/1/', headers=credentials)
        self.assertEqual(res.status_code, 404)
