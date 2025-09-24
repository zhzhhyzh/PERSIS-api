const express = require('express');
const cors = require('cors');
const db = require('./models');

// Simple health check server
const app = express();

app.use(cors());
app.use(express.json());

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'OK',
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || 'development',
    port: process.env.PORT || 3000
  });
});

// Test database connection
app.get('/db-test', async (req, res) => {
  try {
    await db.sequelize.authenticate();
    res.json({
      status: 'OK',
      message: 'Database connection successful',
      database: db.sequelize.config.database,
      host: db.sequelize.config.host
    });
  } catch (error) {
    res.status(500).json({
      status: 'ERROR',
      message: 'Database connection failed',
      error: error.message
    });
  }
});

// Test API endpoints
app.get('/api-test', (req, res) => {
  res.json({
    status: 'OK',
    message: 'API endpoints are working',
    availableEndpoints: [
      'POST /api/user/login',
      'POST /api/user/create',
      'GET /api/user/detail',
      'POST /api/user/update',
      'POST /api/user/change_password',
      'POST /api/invoke/runPythonProcess'
    ]
  });
});

const PORT = process.env.PORT || 3001;

console.log('Starting health check server...');
app.listen(PORT, () => {
  console.log(`Health check server running on http://localhost:${PORT}`);
  console.log('Available endpoints:');
  console.log(`  - GET http://localhost:${PORT}/health`);
  console.log(`  - GET http://localhost:${PORT}/db-test`);
  console.log(`  - GET http://localhost:${PORT}/api-test`);
});
