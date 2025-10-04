/**
 * Main App component
 */
import React from 'react';
import Dashboard from './components/Dashboard';
import './App.css';

const App: React.FC = () => {
  return (
    <div className="App">
      <Dashboard />
    </div>
  );
};

export default App;
