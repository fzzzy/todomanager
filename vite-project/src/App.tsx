import { useState, useEffect } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

interface Todo {
  id: number;
  title: string;
  state: boolean;
}

function App() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [title, setTitle] = useState('');

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

  return (
    <>
      <div>
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Todomanager</h1>
      
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
                <a href={`/${todo.id}/`}>{todo.title}</a>
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
    </>
  )
}

export default App
