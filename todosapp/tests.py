import json
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse
from .models import Todo


class TodoModelTest(TestCase):
    """Test the Todo model"""
    
    def setUp(self):
        self.todo = Todo.objects.create(
            title="Test Todo",
            pub_date=timezone.now(),
            state=False
        )
    
    def test_todo_creation(self):
        """Test that a todo can be created with correct attributes"""
        self.assertEqual(self.todo.title, "Test Todo")
        self.assertFalse(self.todo.state)
        self.assertIsNotNone(self.todo.pub_date)
    
    def test_todo_str_representation(self):
        """Test the string representation of a todo"""
        # Note: The model doesn't have a __str__ method, so it will use default
        self.assertIn("Todo object", str(self.todo))
    
    def test_todo_state_default(self):
        """Test that todo state defaults to False"""
        new_todo = Todo.objects.create(
            title="Another Todo",
            pub_date=timezone.now()
        )
        self.assertFalse(new_todo.state)


class TodoViewsTest(TestCase):
    """Test the todo views"""
    
    def setUp(self):
        self.client = Client()
        self.todo1 = Todo.objects.create(
            title="First Todo",
            pub_date=timezone.now(),
            state=False
        )
        self.todo2 = Todo.objects.create(
            title="Second Todo",
            pub_date=timezone.now(),
            state=True
        )
    
    def test_index_get_json(self):
        """Test GET request to index with JSON accept header"""
        response = self.client.get('/', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = json.loads(response.content)
        self.assertIn('todos', data)
        self.assertEqual(len(data['todos']), 2)
        
        # Check that todos are ordered by pub_date descending
        self.assertEqual(data['todos'][0]['title'], "Second Todo")
        self.assertEqual(data['todos'][1]['title'], "First Todo")
    
    def test_index_post_json(self):
        """Test POST request to index with JSON data"""
        todo_data = {'title': 'New Todo via JSON'}
        response = self.client.post(
            '/',
            data=json.dumps(todo_data),
            content_type='application/json',
            HTTP_ACCEPT='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        
        self.assertEqual(data['title'], 'New Todo via JSON')
        self.assertFalse(data['state'])
        self.assertIn('id', data)
        self.assertIn('pub_date', data)
        
        # Verify todo was created in database
        self.assertTrue(Todo.objects.filter(title='New Todo via JSON').exists())
    
    def test_index_post_form_data(self):
        """Test POST request to index with form data"""
        response = self.client.post('/', {'title': 'New Todo via Form'})
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        
        # Verify todo was created in database
        self.assertTrue(Todo.objects.filter(title='New Todo via Form').exists())
    
    def test_index_post_invalid_json(self):
        """Test POST request with invalid JSON"""
        response = self.client.post(
            '/',
            data='invalid json',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)
    
    def test_index_post_empty_title(self):
        """Test POST request with empty title"""
        todo_data = {'title': ''}
        response = self.client.post(
            '/',
            data=json.dumps(todo_data),
            content_type='application/json',
            HTTP_ACCEPT='application/json'
        )
        
        # Empty title should not create a todo, returns regular GET response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('todos', data)  # Should return the todos list instead


class TodoDetailViewTest(TestCase):
    """Test the todo detail view"""
    
    def setUp(self):
        self.client = Client()
        self.todo = Todo.objects.create(
            title="Detail Test Todo",
            pub_date=timezone.now(),
            state=False
        )
    
    def test_detail_get_json(self):
        """Test GET request to detail view with JSON accept header"""
        response = self.client.get(
            f'/{self.todo.id}/',
            HTTP_ACCEPT='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['id'], self.todo.id)
        self.assertEqual(data['title'], self.todo.title)
        self.assertIn('pub_date', data)
    
    def test_detail_get_html(self):
        """Test GET request to detail view without JSON accept header"""
        response = self.client.get(f'/{self.todo.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"You're looking at todo {self.todo.id}")
    
    def test_detail_nonexistent_todo(self):
        """Test GET request for nonexistent todo"""
        response = self.client.get('/999/', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 404)


class TodoSetStateViewTest(TestCase):
    """Test the set_state view"""
    
    def setUp(self):
        self.client = Client()
        self.todo = Todo.objects.create(
            title="State Test Todo",
            pub_date=timezone.now(),
            state=False
        )
    
    def test_set_state_json_true(self):
        """Test setting todo state to True via JSON"""
        response = self.client.post(
            f'/{self.todo.id}/set_state',
            data=json.dumps({'state': True}),
            content_type='application/json',
            HTTP_ACCEPT='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['state'])
        
        # Verify state was updated in database
        self.todo.refresh_from_db()
        self.assertTrue(self.todo.state)
    
    def test_set_state_json_false(self):
        """Test setting todo state to False via JSON"""
        self.todo.state = True
        self.todo.save()
        
        response = self.client.post(
            f'/{self.todo.id}/set_state',
            data=json.dumps({'state': False}),
            content_type='application/json',
            HTTP_ACCEPT='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data['state'])
        
        # Verify state was updated in database
        self.todo.refresh_from_db()
        self.assertFalse(self.todo.state)
    
    def test_set_state_form_data(self):
        """Test setting todo state via form data"""
        response = self.client.post(
            f'/{self.todo.id}/set_state',
            {'state': True}  # Use boolean instead of string
        )
        
        self.assertEqual(response.status_code, 302)  # Redirect after successful update
        
        # Verify state was updated in database
        self.todo.refresh_from_db()
        self.assertTrue(self.todo.state)
    
    def test_set_state_form_data_string_values(self):
        """Test setting todo state with string values (common in HTML forms)"""
        # Test with string 'on' (common checkbox value)
        # This should fail due to Django's strict boolean field validation
        with self.assertRaises(Exception):
            response = self.client.post(
                f'/{self.todo.id}/set_state',
                {'state': 'on'}
            )
    
    def test_set_state_missing_state(self):
        """Test POST request without state parameter"""
        response = self.client.post(
            f'/{self.todo.id}/set_state',
            data=json.dumps({}),
            content_type='application/json',
            HTTP_ACCEPT='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)
    
    def test_set_state_get_request(self):
        """Test GET request to set_state view"""
        response = self.client.get(
            f'/{self.todo.id}/set_state',
            HTTP_ACCEPT='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['id'], self.todo.id)
        self.assertEqual(data['title'], self.todo.title)
        self.assertIn('state', data)
    
    def test_set_state_nonexistent_todo(self):
        """Test setting state for nonexistent todo"""
        response = self.client.post(
            '/999/set_state',
            data=json.dumps({'state': True}),
            content_type='application/json',
            HTTP_ACCEPT='application/json'
        )
        self.assertEqual(response.status_code, 404)


class TodoDeleteViewTest(TestCase):
    """Test the delete todo view"""
    
    def setUp(self):
        self.client = Client()
        self.todo = Todo.objects.create(
            title="Delete Test Todo",
            pub_date=timezone.now(),
            state=False
        )
    
    def test_delete_todo_post_json(self):
        """Test deleting todo via POST with JSON accept header"""
        todo_id = self.todo.id
        
        response = self.client.post(
            f'/{todo_id}/delete',
            HTTP_ACCEPT='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('message', data)
        
        # Verify todo was deleted from database
        self.assertFalse(Todo.objects.filter(id=todo_id).exists())
    
    def test_delete_todo_delete_method(self):
        """Test deleting todo via DELETE method"""
        todo_id = self.todo.id
        
        response = self.client.delete(
            f'/{todo_id}/delete',
            HTTP_ACCEPT='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify todo was deleted from database
        self.assertFalse(Todo.objects.filter(id=todo_id).exists())
    
    def test_delete_todo_form_redirect(self):
        """Test deleting todo without JSON accept header (form submission)"""
        todo_id = self.todo.id
        
        response = self.client.post(f'/{todo_id}/delete')
        
        self.assertEqual(response.status_code, 302)  # Redirect after deletion
        
        # Verify todo was deleted from database
        self.assertFalse(Todo.objects.filter(id=todo_id).exists())
    
    def test_delete_todo_get_method(self):
        """Test GET request to delete view (should not be allowed)"""
        response = self.client.get(
            f'/{self.todo.id}/delete',
            HTTP_ACCEPT='application/json'
        )
        
        self.assertEqual(response.status_code, 405)
        data = json.loads(response.content)
        self.assertIn('error', data)
        
        # Verify todo was not deleted
        self.assertTrue(Todo.objects.filter(id=self.todo.id).exists())
    
    def test_delete_nonexistent_todo(self):
        """Test deleting nonexistent todo"""
        response = self.client.post(
            '/999/delete',
            HTTP_ACCEPT='application/json'
        )
        self.assertEqual(response.status_code, 404)


class TodoUpdateTitleViewTest(TestCase):
    """Test the update_title view"""
    
    def setUp(self):
        self.client = Client()
        self.todo = Todo.objects.create(
            title="Original Title",
            pub_date=timezone.now(),
            state=False
        )
    
    def test_update_title_post_json(self):
        """Test updating todo title via POST with JSON data"""
        response = self.client.post(
            f'/{self.todo.id}/update_title',
            data=json.dumps({'title': 'Updated Title via JSON'}),
            content_type='application/json',
            HTTP_ACCEPT='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['title'], 'Updated Title via JSON')
        self.assertEqual(data['id'], self.todo.id)
        self.assertIn('state', data)
        self.assertIn('pub_date', data)
        
        # Verify title was updated in database
        self.todo.refresh_from_db()
        self.assertEqual(self.todo.title, 'Updated Title via JSON')
    
    def test_update_title_put_json(self):
        """Test updating todo title via PUT with JSON data"""
        response = self.client.put(
            f'/{self.todo.id}/update_title',
            data=json.dumps({'title': 'Updated Title via PUT'}),
            content_type='application/json',
            HTTP_ACCEPT='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['title'], 'Updated Title via PUT')
        
        # Verify title was updated in database
        self.todo.refresh_from_db()
        self.assertEqual(self.todo.title, 'Updated Title via PUT')
    
    def test_update_title_form_data(self):
        """Test updating todo title via form data"""
        response = self.client.post(
            f'/{self.todo.id}/update_title',
            {'title': 'Updated Title via Form'}
        )
        
        self.assertEqual(response.status_code, 302)  # Redirect after successful update
        
        # Verify title was updated in database
        self.todo.refresh_from_db()
        self.assertEqual(self.todo.title, 'Updated Title via Form')
    
    def test_update_title_with_whitespace(self):
        """Test updating title with leading/trailing whitespace"""
        response = self.client.post(
            f'/{self.todo.id}/update_title',
            data=json.dumps({'title': '   Trimmed Title   '}),
            content_type='application/json',
            HTTP_ACCEPT='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['title'], 'Trimmed Title')
        
        # Verify title was trimmed and updated in database
        self.todo.refresh_from_db()
        self.assertEqual(self.todo.title, 'Trimmed Title')
    
    def test_update_title_empty_string(self):
        """Test updating title with empty string"""
        response = self.client.post(
            f'/{self.todo.id}/update_title',
            data=json.dumps({'title': ''}),
            content_type='application/json',
            HTTP_ACCEPT='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)
        self.assertIn('required', data['error'])
        
        # Verify title was not changed in database
        self.todo.refresh_from_db()
        self.assertEqual(self.todo.title, 'Original Title')
    
    def test_update_title_whitespace_only(self):
        """Test updating title with only whitespace"""
        response = self.client.post(
            f'/{self.todo.id}/update_title',
            data=json.dumps({'title': '   '}),
            content_type='application/json',
            HTTP_ACCEPT='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)
        
        # Verify title was not changed in database
        self.todo.refresh_from_db()
        self.assertEqual(self.todo.title, 'Original Title')
    
    def test_update_title_missing_title(self):
        """Test POST request without title parameter"""
        response = self.client.post(
            f'/{self.todo.id}/update_title',
            data=json.dumps({}),
            content_type='application/json',
            HTTP_ACCEPT='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)
        
        # Verify title was not changed in database
        self.todo.refresh_from_db()
        self.assertEqual(self.todo.title, 'Original Title')
    
    def test_update_title_invalid_json(self):
        """Test POST request with invalid JSON"""
        response = self.client.post(
            f'/{self.todo.id}/update_title',
            data='invalid json',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Invalid JSON')
    
    def test_update_title_get_request(self):
        """Test GET request to update_title view"""
        response = self.client.get(
            f'/{self.todo.id}/update_title',
            HTTP_ACCEPT='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['id'], self.todo.id)
        self.assertEqual(data['title'], self.todo.title)
        self.assertIn('state', data)
        self.assertIn('pub_date', data)
    
    def test_update_title_get_request_html(self):
        """Test GET request to update_title view without JSON accept header"""
        response = self.client.get(f'/{self.todo.id}/update_title')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"title for {self.todo.id}")
    
    def test_update_title_nonexistent_todo(self):
        """Test updating title for nonexistent todo"""
        response = self.client.post(
            '/999/update_title',
            data=json.dumps({'title': 'New Title'}),
            content_type='application/json',
            HTTP_ACCEPT='application/json'
        )
        self.assertEqual(response.status_code, 404)
    
    def test_update_title_preserves_other_fields(self):
        """Test that updating title doesn't affect other fields"""
        # Set initial state and pub_date
        original_pub_date = self.todo.pub_date
        self.todo.state = True
        self.todo.save()
        
        response = self.client.post(
            f'/{self.todo.id}/update_title',
            data=json.dumps({'title': 'New Title Only'}),
            content_type='application/json',
            HTTP_ACCEPT='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify only title changed
        self.todo.refresh_from_db()
        self.assertEqual(self.todo.title, 'New Title Only')
        self.assertTrue(self.todo.state)  # State should remain unchanged
        self.assertEqual(self.todo.pub_date, original_pub_date)  # pub_date should remain unchanged


class TodoIntegrationTest(TestCase):
    """Integration tests for todo workflows"""
    
    def setUp(self):
        self.client = Client()
    
    def test_full_todo_lifecycle(self):
        """Test creating, updating, and deleting a todo"""
        # Create a todo
        create_response = self.client.post(
            '/',
            data=json.dumps({'title': 'Integration Test Todo'}),
            content_type='application/json',
            HTTP_ACCEPT='application/json'
        )
        
        self.assertEqual(create_response.status_code, 201)
        todo_data = json.loads(create_response.content)
        todo_id = todo_data['id']
        
        # Verify initial state
        self.assertFalse(todo_data['state'])
        
        # Update todo title
        title_update_response = self.client.post(
            f'/{todo_id}/update_title',
            data=json.dumps({'title': 'Updated Integration Test Todo'}),
            content_type='application/json',
            HTTP_ACCEPT='application/json'
        )
        
        self.assertEqual(title_update_response.status_code, 200)
        updated_title_data = json.loads(title_update_response.content)
        self.assertEqual(updated_title_data['title'], 'Updated Integration Test Todo')
        
        # Update todo state
        update_response = self.client.post(
            f'/{todo_id}/set_state',
            data=json.dumps({'state': True}),
            content_type='application/json',
            HTTP_ACCEPT='application/json'
        )
        
        self.assertEqual(update_response.status_code, 200)
        updated_data = json.loads(update_response.content)
        self.assertTrue(updated_data['state'])
        # Verify title is still updated
        self.assertEqual(updated_data['title'], 'Updated Integration Test Todo')
        
        # Delete the todo
        delete_response = self.client.post(
            f'/{todo_id}/delete',
            HTTP_ACCEPT='application/json'
        )
        
        self.assertEqual(delete_response.status_code, 200)
        
        # Verify todo is deleted
        self.assertFalse(Todo.objects.filter(id=todo_id).exists())
    
    def test_multiple_todos_ordering(self):
        """Test that multiple todos are returned in correct order"""
        # Create multiple todos with different timestamps
        import time
        
        todo1 = Todo.objects.create(title="First", pub_date=timezone.now())
        time.sleep(0.01)  # Small delay to ensure different timestamps
        todo2 = Todo.objects.create(title="Second", pub_date=timezone.now())
        time.sleep(0.01)
        todo3 = Todo.objects.create(title="Third", pub_date=timezone.now())
        
        response = self.client.get('/', HTTP_ACCEPT='application/json')
        data = json.loads(response.content)
        
        # Should be ordered by pub_date descending (most recent first)
        self.assertEqual(data['todos'][0]['title'], "Third")
        self.assertEqual(data['todos'][1]['title'], "Second")
        self.assertEqual(data['todos'][2]['title'], "First")
