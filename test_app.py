import unittest
import app
import json

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.app.test_client()

    def test_hello_endpoint(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Hello from Jenkins', response.data)

    def test_health_endpoint(self):
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['service'], 'python-app')

if __name__ == '__main__':
    unittest.main()
