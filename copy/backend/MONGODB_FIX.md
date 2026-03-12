# MongoDB Connection Fixes

If you encounter issues connecting to MongoDB (especially on Windows or with DNS resolution), consider the following:

1. **DNS Resolution**: If `MONGO_URL` uses `localhost`, try `127.0.0.1` if you are running MongoDB locally.
2. **TLS/SSL**: If using MongoDB Atlas, ensure `tlsAllowInvalidCertificates=True` is used in the connection string or client options if you face certificate verification issues in development.
3. **Environment Variables**: Ensure `MONGO_URL` is correctly set in your `.env` file.
4. **Network Access**: For Atlas, ensure your IP address is whitelisted in the MongoDB Atlas dashboard.
