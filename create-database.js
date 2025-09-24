const mysql = require('mysql2/promise');

async function createDatabase() {
  try {
    // Connect to MySQL without specifying a database
    const connection = await mysql.createConnection({
      host: '127.0.0.1',
      user: 'root',
      password: null // No password as configured
    });

    console.log('Connected to MySQL server');

    // Create the database if it doesn't exist
    await connection.execute('CREATE DATABASE IF NOT EXISTS persis');
    console.log('✅ Database "persis" created successfully or already exists');

    // Close the connection
    await connection.end();
    console.log('Connection closed');

  } catch (error) {
    console.error('❌ Error creating database:', error.message);
    
    if (error.code === 'ER_ACCESS_DENIED_ERROR') {
      console.log('\n💡 Possible solutions:');
      console.log('1. Check if MySQL root user has a password');
      console.log('2. Try running: mysql -u root -p');
      console.log('3. Update config.json with correct MySQL credentials');
    }
  }
}

createDatabase();
