import React, { useState } from 'react';

function App() {
  const [folderPath, setFolderPath] = useState('');
  const [status, setStatus] = useState(null);

  const handleStart = async () => {
    const res = await fetch('http://localhost:5000/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ folderPath })
    });
    const data = await res.json();
    setStatus(data);
  };

  const handleStop = async () => {
    const res = await fetch('http://localhost:5000/stop', {
      method: 'POST'
    });
    const data = await res.json();
    setStatus(data);
  };

  const checkStatus = async () => {
    const res = await fetch('http://localhost:5000/status');
    const data = await res.json();
    setStatus(data);
  };

  return (
    <div style={{ padding: 24, fontFamily: 'Arial, sans-serif', maxWidth: 800 }}>
      <h1>Certified Human Made</h1>

      <input
        type="text"
        placeholder="Path to Ableton Project Folder"
        value={folderPath}
        onChange={(e) => setFolderPath(e.target.value)}
        style={{ width: '100%', padding: 8, marginBottom: 12 }}
      />

      <div style={{ display: 'flex', gap: 10 }}>
        <button onClick={handleStart}>Start</button>
        <button onClick={handleStop}>Stop</button>
        <button onClick={checkStatus}>Check Status</button>
      </div>

      <pre style={{ marginTop: 20, background: '#eee', padding: 12 }}>
        {status ? JSON.stringify(status, null, 2) : 'No status yet'}
      </pre>
    </div>
  );
}

export default App;
