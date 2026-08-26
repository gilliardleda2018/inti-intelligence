import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Plot from 'react-plotly.js';
import './styles.css';

function App() {
  const [sentimentData, setSentimentData] = useState([]);

  useEffect(() => {
    // Adjust the base URL if the API is hosted elsewhere
    axios.get('/api/sentiment')
      .then(res => setSentimentData(res.data))
      .catch(err => console.error('Error loading sentiment data', err));
  }, []);

  const chartData = {
    type: 'pie',
    values: sentimentData.map(d => d.sentiment_score),
    labels: sentimentData.map(d => d.review_text.slice(0, 30) + '...'),
    textinfo: 'label+percent',
    hoverinfo: 'label+value',
  };

  return (
    <div className="app-container">
      <header className="header">
        <img src="/logo.png" alt="INTI" className="logo" />
        <h1>INTI Intelligence Dashboard</h1>
      </header>
      <section className="content">
        <h2>Sentiment Analysis</h2>
        {sentimentData.length > 0 ? (
          <Plot data={[chartData]} layout={{ title: 'Sentiment Scores', width: 600, height: 400 }} />
        ) : (
          <p>Carregando dados...</p>
        )}
      </section>
    </div>
  );
}

export default App;
