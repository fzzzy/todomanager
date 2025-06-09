// Utility functions for the Todo app

export interface Todo {
  id: number;
  title: string;
  state: boolean;
}

export const validateTodoTitle = (title: string): string | null => {
  const trimmed = title.trim();
  if (!trimmed) {
    return 'Todo title cannot be empty';
  }
  if (trimmed.length > 255) {
    return 'Todo title cannot exceed 255 characters';
  }
  return null;
};

export const formatTodoForDisplay = (todo: Todo): string => {
  const status = todo.state ? '✓' : '○';
  return `${status} ${todo.title}`;
};

export const filterTodos = (todos: Todo[], filter: 'all' | 'active' | 'completed'): Todo[] => {
  switch (filter) {
    case 'active':
      return todos.filter(todo => !todo.state);
    case 'completed':
      return todos.filter(todo => todo.state);
    default:
      return todos;
  }
};

export const getTodoStats = (todos: Todo[]): { total: number; completed: number; active: number } => {
  const total = todos.length;
  const completed = todos.filter(todo => todo.state).length;
  const active = total - completed;
  
  return { total, completed, active };
};

export const sortTodos = (todos: Todo[], sortBy: 'title' | 'state' | 'id'): Todo[] => {
  return [...todos].sort((a, b) => {
    switch (sortBy) {
      case 'title':
        return a.title.localeCompare(b.title);
      case 'state':
        return Number(a.state) - Number(b.state);
      case 'id':
      default:
        return a.id - b.id;
    }
  });
};
