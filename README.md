# Sonificafy Backend

This is the backend server for the Sonificafy project, which processes frontend requests and handles data sonification.

## 🚀 Technologies

The project uses a hybrid architecture with:

- **Node.js**: For the REST API server
- **Python**: For data processing and sonification

## 📋 Prerequisites

- Node.js (v18 or higher)
- Python (v3.8 or higher)
- npm or yarn
- pip (Python package manager)

## 🔧 Installation

1. Clone the repository:

```bash
git clone https://github.com/alejandromur/sonificafy-backend.git
cd sonificafy-backend
```

2. Install Node.js dependencies:

```bash
npm install
```

3. Install Python dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

- Copy `.env.example` to `.env`
- Adjust the variables according to your environment

## 🚀 Development

To start the server in development mode:

```bash
npm run dev
```

The server will start at `http://localhost:3000` (or the port specified in the environment variables).

## 📦 Project Structure

```
sonificafy-backend/
├── src/           # Node.js source code
├── scripts/       # Python sonification scripts
├── audios/        # Generated audio files directory
├── .env           # Environment variables
└── requirements.txt # Python dependencies
```

## 📚 Main Dependencies

### Node.js

- express: Web framework
- cors: CORS middleware
- dotenv: Environment variables management
- axios: HTTP client

### Python

- numpy: Numerical processing
- scipy: Signal processing

## 📄 License

This project is under the MIT License - see the [LICENSE](LICENSE) file for details.

## ✍️ Author

Alejandro - [alejandro@mamutlove.com](mailto:alejandro@mamutlove.com)

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a new branch (`git switch -c feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

Please make sure to:

- Follow the existing code style
- Add comments to your code where necessary
- Update the documentation if needed
- Test your changes before submitting
