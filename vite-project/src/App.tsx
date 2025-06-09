import { useState, useEffect } from 'react'
import './App.css'

interface Todo {
  id: number;
  title: string;
  state: boolean;
}

function App() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [title, setTitle] = useState('');
  const [editingTitles, setEditingTitles] = useState<{[key: number]: string}>({});

  const getTitleValue = (todoId: number, originalTitle: string): string => {
    const editingTitle = editingTitles[todoId];
    return editingTitle !== undefined ? editingTitle : originalTitle;
  };

  useEffect(() => {
    const fetchTodos = async () => {
      try {
        const response = await fetch('/', {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
          },
        });
        
        if (response.ok) {
          const todosData = await response.json();
          setTodos(todosData.todos);
        }
      } catch (error) {
        console.error('Error fetching todos:', error);
      }
    };

    fetchTodos();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const trimmedTitle = title.trim();
    if (!trimmedTitle) {
      alert('Please enter a todo title');
      return;
    }

    try {
      const response = await fetch('/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          title: trimmedTitle
        })
      });
      
      if (response.ok) {
        const newTodo = await response.json();
        setTodos(prevTodos => [...prevTodos, newTodo]);
        setTitle('');
      }
    } catch (error) {
      console.error('Error adding todo:', error);
    }
  };

  const handleStateChange = async (todoId: number, newState: boolean) => {
    try {
      const response = await fetch(`/${todoId}/set_state`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          state: newState
        })
      });
      
      if (response.ok) {
        const updatedTodo = await response.json();
        setTodos(prevTodos => 
          prevTodos.map(todo => 
            todo.id === todoId ? { ...todo, state: updatedTodo.state } : todo
          )
        );
      }
    } catch (error) {
      console.error('Error updating todo state:', error);
    }
  };

  const handleDelete = async (todoId: number) => {
    try {
      const response = await fetch(`/${todoId}/delete`, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
        },
      });
      
      if (response.ok) {
        setTodos(prevTodos => prevTodos.filter(todo => todo.id !== todoId));
      }
    } catch (error) {
      console.error('Error deleting todo:', error);
    }
  };

  const handleTitleChange = (todoId: number, newTitle: string) => {
    setEditingTitles(prev => ({
      ...prev,
      [todoId]: newTitle
    }));
  };

  const handleTitleBlur = async (todoId: number) => {
    const newTitle = editingTitles[todoId];
    
    // If not currently editing, nothing to do
    if (newTitle === undefined) return;

    const trimmedTitle = newTitle.trim();
    const originalTodo = todos.find(todo => todo.id === todoId);
    
    if (!trimmedTitle || !originalTodo) {
      // Reset to original title if empty - just clear editing state
      setEditingTitles(prev => {
        const updated = { ...prev };
        delete updated[todoId];
        return updated;
      });
      return;
    }

    // Check if title actually changed
    if (originalTodo.title === trimmedTitle) {
      // No change, just clear editing state
      setEditingTitles(prev => {
        const updated = { ...prev };
        delete updated[todoId];
        return updated;
      });
      return;
    }

    try {
      const response = await fetch(`/${todoId}/update_title`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          title: trimmedTitle
        })
      });
      
      if (response.ok) {
        const updatedTodo = await response.json();
        setTodos(prevTodos => 
          prevTodos.map(todo => 
            todo.id === todoId ? { ...todo, title: updatedTodo.title } : todo
          )
        );
        // Clear editing state
        setEditingTitles(prev => {
          const updated = { ...prev };
          delete updated[todoId];
          return updated;
        });
      }
    } catch (error) {
      console.error('Error updating todo title:', error);
      // Reset to original title on error
      setEditingTitles(prev => {
        const updated = { ...prev };
        delete updated[todoId];
        return updated;
      });
    }
  };

  const handleLogout = async () => {
    try {
      const response = await fetch('/logout/', {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
        },
      });
      
      if (response.ok) {
        // Redirect to login page or reload the page
        window.location.href = '/login/';
      }
    } catch (error) {
      console.error('Error logging out:', error);
    }
  };

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>Todomanager</h1>
      </div>
      
      <div id="todos-container">
        {todos.length > 0 ? (
          <ul id="todos-list">
            {todos.map(todo => (
              <li key={todo.id}>
                <input
                  type="checkbox"
                  checked={todo.state}
                  onChange={(e) => handleStateChange(todo.id, e.target.checked)}
                />
                <input
                  type="text"
                  value={getTitleValue(todo.id, todo.title)}
                  onChange={(e) => handleTitleChange(todo.id, e.target.value)}
                  onBlur={() => handleTitleBlur(todo.id)}
                  style={{ 
                    border: 'none', 
                    background: 'transparent', 
                    fontSize: 'inherit',
                    marginLeft: '8px',
                    marginRight: '8px',
                    minWidth: '200px'
                  }}
                />
                <button 
                  onClick={() => handleDelete(todo.id)}
                  style={{ marginLeft: '10px', color: 'red', cursor: 'pointer' }}
                >
                  Delete
                </button>
              </li>
            ))}
          </ul>
        ) : (
          <p id="no-todos">No todos are available.</p>
        )}
      </div>

      <form id="todo-form" onSubmit={handleSubmit}>
        <input
          type="text"
          id="title-input"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Enter todo title"
          required
        />
        <button type="submit">Add Todo</button>
      </form>

      <button 
        onClick={handleLogout}
        style={{ marginTop: '20px', color: 'blue', cursor: 'pointer' }}
      >
        Logout
      </button>
    </>
  )
}

export default App
