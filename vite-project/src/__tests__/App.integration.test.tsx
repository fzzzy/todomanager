import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { jest } from '@jest/globals';
import App from '../App';

// Mock fetch
const mockFetch = jest.fn() as any;
(global as any).fetch = mockFetch;

// Mock alert
const mockAlert = jest.fn();
(global as any).alert = mockAlert;

describe('App Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockFetch.mockClear();
    mockAlert.mockClear();
  });

  describe('Complete user workflows', () => {
    it('should handle a complete todo lifecycle: add, edit, toggle, delete', async () => {
      const user = userEvent.setup();
      
      // Initial empty state
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ todos: [] }),
      });

      render(<App />);

      // Verify empty state
      await waitFor(() => {
        expect(screen.getByText('No todos are available.')).toBeInTheDocument();
      });

      // Add a new todo
      const newTodo = { id: 1, title: 'New Todo', state: false };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => newTodo,
      });

      const input = screen.getByPlaceholderText('Enter todo title');
      const submitButton = screen.getByRole('button', { name: 'Add Todo' });

      await user.type(input, 'New Todo');
      await user.click(submitButton);

      // Verify todo appears
      await waitFor(() => {
        expect(screen.getByDisplayValue('New Todo')).toBeInTheDocument();
        expect(screen.queryByText('No todos are available.')).not.toBeInTheDocument();
      });

      // Edit the todo title
      const updatedTodo = { id: 1, title: 'Updated Todo', state: false };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => updatedTodo,
      });

      const titleInput = screen.getByDisplayValue('New Todo');
      await user.clear(titleInput);
      await user.type(titleInput, 'Updated Todo');
      await user.tab(); // Trigger blur

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith('/1/update_title', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          body: JSON.stringify({ title: 'Updated Todo' }),
        });
      });

      // Toggle todo state
      const toggledTodo = { id: 1, title: 'Updated Todo', state: true };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => toggledTodo,
      });

      const checkbox = screen.getByRole('checkbox');
      await user.click(checkbox);

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith('/1/set_state', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          body: JSON.stringify({ state: true }),
        });
      });

      // Delete the todo
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({}),
      });

      const deleteButton = screen.getByText('Delete');
      await user.click(deleteButton);

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith('/1/delete', {
          method: 'POST',
          headers: {
            'Accept': 'application/json',
          },
        });
      });
    });

    it('should handle multiple todos simultaneously', async () => {
      const user = userEvent.setup();
      
      // Initial state with multiple todos
      const initialTodos = [
        { id: 1, title: 'Todo 1', state: false },
        { id: 2, title: 'Todo 2', state: true },
        { id: 3, title: 'Todo 3', state: false },
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ todos: initialTodos }),
      });

      render(<App />);

      // Verify all todos are displayed
      await waitFor(() => {
        expect(screen.getByDisplayValue('Todo 1')).toBeInTheDocument();
        expect(screen.getByDisplayValue('Todo 2')).toBeInTheDocument();
        expect(screen.getByDisplayValue('Todo 3')).toBeInTheDocument();
      });

      // Verify checkboxes reflect the correct states
      const checkboxes = screen.getAllByRole('checkbox');
      expect(checkboxes[0]).not.toBeChecked(); // Todo 1
      expect(checkboxes[1]).toBeChecked();     // Todo 2
      expect(checkboxes[2]).not.toBeChecked(); // Todo 3

      // Toggle multiple todos
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: 1, title: 'Todo 1', state: true }),
      });

      await user.click(checkboxes[0]); // Toggle Todo 1

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith('/1/set_state', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          body: JSON.stringify({ state: true }),
        });
      });
    });
  });

  describe('Error scenarios', () => {
    it('should handle network failures gracefully', async () => {
      const user = userEvent.setup();
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

      // Initial load succeeds
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ todos: [] }),
      });

      render(<App />);

      // Add todo fails
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      const input = screen.getByPlaceholderText('Enter todo title');
      const submitButton = screen.getByRole('button', { name: 'Add Todo' });

      await user.type(input, 'Failed Todo');
      await user.click(submitButton);

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('Error adding todo:', expect.any(Error));
      });

      // Input should not be cleared on error
      expect(input).toHaveValue('Failed Todo');

      consoleSpy.mockRestore();
    });

    it('should handle server errors (non-ok responses)', async () => {
      const user = userEvent.setup();

      // Initial load succeeds
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ todos: [] }),
      });

      render(<App />);

      // Add todo returns server error
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
      });

      const input = screen.getByPlaceholderText('Enter todo title');
      const submitButton = screen.getByRole('button', { name: 'Add Todo' });

      await user.type(input, 'Server Error Todo');
      await user.click(submitButton);

      // The todo should not be added to the UI since the response was not ok
      await waitFor(() => {
        expect(screen.queryByDisplayValue('Server Error Todo')).toBeInTheDocument();
      });
      
      // Input should not be cleared on server error
      expect(screen.getByDisplayValue('Server Error Todo')).toBeInTheDocument();
    });
  });

  describe('Form validation and UX', () => {
    beforeEach(() => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ todos: [] }),
      });
    });

    it('should handle form submission with Enter key', async () => {
      const user = userEvent.setup();
      const newTodo = { id: 1, title: 'Enter Key Todo', state: false };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => newTodo,
      });

      render(<App />);

      const input = screen.getByPlaceholderText('Enter todo title');
      await user.type(input, 'Enter Key Todo');
      await user.keyboard('{Enter}');

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith('/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          body: JSON.stringify({ title: 'Enter Key Todo' }),
        });
      });
    });

    it('should have proper form validation attributes', async () => {
      render(<App />);

      const input = screen.getByPlaceholderText('Enter todo title');
      expect(input).toHaveAttribute('required');
      expect(input).toHaveAttribute('type', 'text');
    });

    it('should handle whitespace-only input', async () => {
      const user = userEvent.setup();

      render(<App />);

      const input = screen.getByPlaceholderText('Enter todo title');
      const submitButton = screen.getByRole('button', { name: 'Add Todo' });

      await user.type(input, '   ');
      await user.click(submitButton);

      expect(mockAlert).toHaveBeenCalledWith('Please enter a todo title');
    });
  });

  test('complete edit title workflow with various scenarios', async () => {
    const mockTodos = [
      { id: 1, title: 'Original Todo', completed: false },
      { id: 2, title: 'Another Todo', completed: true },
    ];

    // Mock initial fetch
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ todos: mockTodos }),
    });

    render(<App />);

    // Wait for todos to load
    await waitFor(() => {
      expect(screen.getByDisplayValue('Original Todo')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Another Todo')).toBeInTheDocument();
    });

    // Test editing first todo
    const firstTodoInput = screen.getByDisplayValue('Original Todo');
    
    // Start editing
    fireEvent.focus(firstTodoInput);
    fireEvent.change(firstTodoInput, { target: { value: 'Edited Todo Title' } });

    // Mock successful update
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true }),
    });

    // Mock refetch after edit
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ 
        todos: [
          { id: 1, title: 'Edited Todo Title', completed: false },
          { id: 2, title: 'Another Todo', completed: true },
        ]
      }),
    });

    // Finish editing
    fireEvent.blur(firstTodoInput);

    // Verify update API was called
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/1/update_title',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
          body: JSON.stringify({ title: 'Edited Todo Title' }),
        })
      );
    });

    // Test editing second todo with same title (no change)
    const secondTodoInput = screen.getByDisplayValue('Another Todo');
    fireEvent.focus(secondTodoInput);
    fireEvent.change(secondTodoInput, { target: { value: 'Another Todo' } }); // Same value
    fireEvent.blur(secondTodoInput);

    // Should not make additional API call since value didn't change
    expect(global.fetch).toHaveBeenCalledTimes(2); // initial fetch + update (no refetch after successful update)

    // Test editing with empty title (should prevent save)
    fireEvent.focus(firstTodoInput);
    fireEvent.change(firstTodoInput, { target: { value: '' } });
    fireEvent.blur(firstTodoInput);

    // Should not make API call for empty title
    expect(global.fetch).toHaveBeenCalledTimes(2); // No additional calls
  });
});
