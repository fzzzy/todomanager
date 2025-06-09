import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { jest } from '@jest/globals';
import App from '../App';

// Get the mocked fetch
const mockFetch = jest.fn() as any;
(global as any).fetch = mockFetch;

// Mock alert
const mockAlert = jest.fn();
(global as any).alert = mockAlert;

// Helper to create mock Response
const createMockResponse = (data: any, ok = true): Response => {
  return {
    ok,
    json: async () => data,
    status: ok ? 200 : 500,
    statusText: ok ? 'OK' : 'Internal Server Error',
  } as Response;
};

describe('App Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockFetch.mockClear();
    mockAlert.mockClear();
  });

  describe('Initial render and data fetching', () => {
    it('renders the todo manager title', async () => {
      mockFetch.mockResolvedValueOnce(createMockResponse({ todos: [] }));

      render(<App />);
      expect(screen.getByText('Todomanager')).toBeInTheDocument();
      
      // Wait for the async fetch to complete
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith('/', expect.objectContaining({
          method: 'GET',
          headers: { 'Accept': 'application/json' }
        }));
      });
    });

    it('renders main heading correctly', async () => {
      mockFetch.mockResolvedValueOnce(createMockResponse({ todos: [] }));

      render(<App />);
      expect(screen.getByText('Todomanager')).toBeInTheDocument();
      
      // Wait for the async fetch to complete
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith('/', expect.objectContaining({
          method: 'GET',
          headers: { 'Accept': 'application/json' }
        }));
      });
    });

    it('fetches todos on component mount', async () => {
      const mockTodos = [
        { id: 1, title: 'Test Todo 1', state: false },
        { id: 2, title: 'Test Todo 2', state: true },
      ];

      mockFetch.mockResolvedValueOnce(createMockResponse({ todos: mockTodos }));

      render(<App />);

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith('/', {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
          },
        });
      });
    });

    it('displays "No todos are available" when no todos exist', async () => {
      mockFetch.mockResolvedValueOnce(createMockResponse({ todos: [] }));

      render(<App />);

      await waitFor(() => {
        expect(screen.getByText('No todos are available.')).toBeInTheDocument();
      });
    });

    it('displays todos when they exist', async () => {
      const mockTodos = [
        { id: 1, title: 'Test Todo 1', state: false },
        { id: 2, title: 'Test Todo 2', state: true },
      ];

      mockFetch.mockResolvedValueOnce(createMockResponse({ todos: mockTodos }));

      render(<App />);

      await waitFor(() => {
        expect(screen.getByDisplayValue('Test Todo 1')).toBeInTheDocument();
        expect(screen.getByDisplayValue('Test Todo 2')).toBeInTheDocument();
      });
    });
  });

  describe('Adding todos', () => {
    beforeEach(() => {
      mockFetch.mockResolvedValueOnce(createMockResponse({ todos: [] }));
    });

    it('renders the add todo form', () => {
      render(<App />);
      
      expect(screen.getByPlaceholderText('Enter todo title')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Add Todo' })).toBeInTheDocument();
    });

    it('adds a new todo when form is submitted', async () => {
      const user = userEvent.setup();
      const newTodo = { id: 1, title: 'New Todo', state: false };

      mockFetch.mockResolvedValueOnce(createMockResponse(newTodo));

      render(<App />);

      const input = screen.getByPlaceholderText('Enter todo title');
      const submitButton = screen.getByRole('button', { name: 'Add Todo' });

      await user.type(input, 'New Todo');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockFetch).toHaveBeenLastCalledWith('/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          body: JSON.stringify({ title: 'New Todo' }),
        });
      });
    });

    it('has proper form validation attributes', async () => {
      render(<App />);

      const input = screen.getByPlaceholderText('Enter todo title');
      expect(input).toHaveAttribute('required');
      expect(input).toHaveAttribute('type', 'text');
    });
  });

  describe('Error handling', () => {
    it('handles fetch error on initial load', async () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      render(<App />);

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('Error fetching todos:', expect.any(Error));
      });

      consoleSpy.mockRestore();
    });
  });

  test('should handle edit title functionality', async () => {
    const mockTodos = [
      { id: 1, title: 'Test Todo 1', completed: false },
      { id: 2, title: 'Test Todo 2', completed: true },
    ];

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ todos: mockTodos }),
    });

    render(<App />);

    await waitFor(() => {
      expect(screen.getByDisplayValue('Test Todo 1')).toBeInTheDocument();
    });

    // Get the first todo input and simulate editing
    const todoInput = screen.getByDisplayValue('Test Todo 1');
    
    // Clear the input and type new value
    fireEvent.change(todoInput, { target: { value: '' } });
    fireEvent.change(todoInput, { target: { value: 'Updated Todo 1' } });

    // Mock successful update
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true }),
    });

    // Simulate blur to trigger save
    fireEvent.blur(todoInput);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/1/update_title',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
          body: JSON.stringify({ title: 'Updated Todo 1' }),
        })
      );
    });
  });

  test('should handle edit title with no changes (clear editing state)', async () => {
    const mockTodos = [
      { id: 1, title: 'Test Todo 1', completed: false },
    ];

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ todos: mockTodos }),
    });

    render(<App />);

    await waitFor(() => {
      expect(screen.getByDisplayValue('Test Todo 1')).toBeInTheDocument();
    });

    const todoInput = screen.getByDisplayValue('Test Todo 1');

    // Type the same value (no change)
    fireEvent.change(todoInput, { target: { value: 'Test Todo 1' } });
    fireEvent.blur(todoInput);

    // Should not make API call since value didn't change
    expect(global.fetch).toHaveBeenCalledTimes(1); // Only initial fetch
  });

  test('should handle edit title error and reset to original', async () => {
    // Mock console.error
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

    const mockTodos = [
      { id: 1, title: 'Test Todo 1', completed: false },
    ];

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ todos: mockTodos }),
    });

    render(<App />);

    await waitFor(() => {
      expect(screen.getByDisplayValue('Test Todo 1')).toBeInTheDocument();
    });

    const todoInput = screen.getByDisplayValue('Test Todo 1');
    
    // Change the input value
    fireEvent.change(todoInput, { target: { value: 'Updated Todo 1' } });

    // Mock update failure
    (global.fetch as any).mockRejectedValueOnce(new Error('Update failed'));

    // Simulate blur to trigger save
    fireEvent.blur(todoInput);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/1/update_title',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
          body: JSON.stringify({ title: 'Updated Todo 1' }),
        })
      );
    });

    // Should have logged error
    expect(consoleSpy).toHaveBeenCalledWith('Error updating todo title:', expect.any(Error));
    
    // Cleanup
    consoleSpy.mockRestore();
  });

  test('should handle failed update response (non-ok)', async () => {
    const mockTodos = [
      { id: 1, title: 'Test Todo 1', completed: false },
    ];

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ todos: mockTodos }),
    });

    render(<App />);

    await waitFor(() => {
      expect(screen.getByDisplayValue('Test Todo 1')).toBeInTheDocument();
    });

    const todoInput = screen.getByDisplayValue('Test Todo 1');
    
    // Change the input value
    fireEvent.change(todoInput, { target: { value: 'Updated Todo 1' } });

    // Mock update failure with non-ok response
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 500,
    });

    // Simulate blur to trigger save
    fireEvent.blur(todoInput);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/1/update_title',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
          body: JSON.stringify({ title: 'Updated Todo 1' }),
        })
      );
    });
  });
});
