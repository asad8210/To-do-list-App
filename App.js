// App.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [todos, setTodos] = useState([]);

  useEffect(() => {
    fetchTodos();
  }, []);

  const fetchTodos = async () => {
    try {
      const response = await axios.post('http://localhost:5000/graphql', {
        query: `
          {
            todos {
              id
              title
              description
              time
              images
            }
          }
        `
      });
      setTodos(response.data.data.todos);
    } catch (error) {
      console.error('Error fetching todos:', error);
    }
  };

  return (
    <div>
      <h1>To-Do List</h1>
      <ul>
        {todos.map(todo => (
          <li key={todo.id}>
            <h3>{todo.title}</h3>
            <p>{todo.description}</p>
            <p>{todo.time}</p>
            <button onClick={() => deleteTodo(todo.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );

  async function deleteTodo(id) {
    try {
      await axios.post('http://localhost:5000/graphql', {
        query: `
          mutation DeleteTodo($id: Int!) {
            delete_todo(id: $id) {
              success
            }
          }
        `,
        variables: { id }
      });
      // Refetch todos after deletion
      fetchTodos();
    } catch (error) {
      console.error('Error deleting todo:', error);
    }
  }
}

export default App;
