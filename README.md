# Port Pairs SpotOn API

A FastAPI-based REST API for querying CMA CGM port pair booking data.

## Features

- 🚀 Fast API endpoints for port pair data retrieval
- 📊 Query specific port pairs or search by origin/destination
- 🔍 Get lists of all available port pairs and dates
- ✅ Health check endpoint for monitoring
- 🌐 CORS enabled for frontend integration

## API Endpoints

### Core Endpoints

- `GET /` - API information and available endpoints
- `GET /health` - Health check (returns service status)
- `GET /port-pairs` - List all available port pairs
- `GET /port-pairs/{port_pair}` - Get data for specific port pair (e.g., `/port-pairs/BJCOO-BRPEC`)
- `GET /dates` - List all available dates
- `GET /search?origin={code}&destination={code}` - Search port pairs by origin/destination

### Example Usage

```bash
# Get all port pairs
curl https://your-app.railway.app/port-pairs

# Get specific port pair data
curl https://your-app.railway.app/port-pairs/BJCOO-BRPEC

# Search by origin
curl https://your-app.railway.app/search?origin=CIABJ

# Search by destination
curl https://your-app.railway.app/search?destination=BRPEC

# Health check
curl https://your-app.railway.app/health
```

## Local Development Setup

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Step-by-Step Setup

1. **Clone or navigate to the project directory**

   ```bash
   cd /path/to/SpotOn
   ```

2. **Create a virtual environment**

   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment**

   On macOS/Linux:

   ```bash
   source venv/bin/activate
   ```

   On Windows:

   ```bash
   venv\Scripts\activate
   ```

4. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**

   ```bash
   python main.py
   ```

   Or using uvicorn directly:

   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the API**
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

## Deployment to Railway

### Quick Deploy

1. **Install Railway CLI** (optional, but recommended)

   ```bash
   npm i -g @railway/cli
   ```

2. **Login to Railway**

   ```bash
   railway login
   ```

3. **Initialize and deploy**
   ```bash
   railway init
   railway up
   ```

### Deploy via GitHub (Recommended)

1. Push your code to a GitHub repository
2. Go to [Railway.app](https://railway.app)
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway will automatically detect the Procfile and deploy

### Environment Variables (Optional)

If needed, you can set environment variables in Railway dashboard:

- `PORT` - Port number (Railway sets this automatically)

## Project Structure

```
SpotOn/
├── main.py                               # FastAPI application
├── requirements.txt                       # Python dependencies
├── Procfile                              # Railway deployment config
├── .python-version                       # Python version specification
├── .gitignore                            # Git ignore rules
├── README.md                             # This file
├── POLPODS.py                            # Original script (can be removed)
└── Qlik Sense Port Pairs SpotOn.csv     # Data file
```

## Data Format

The API expects a CSV file (`Qlik Sense Port Pairs SpotOn.csv`) with:

- First row: header with dates
- First column: POL-POD Booked (port pair identifiers in format: ORIGIN-DESTINATION)
- Data: percentage values for each date

## Tech Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **Uvicorn** - ASGI server for running the application
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical computing support

## Development Tips

### Viewing Interactive API Docs

FastAPI automatically generates interactive API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Testing Endpoints

You can test all endpoints directly from the Swagger UI at `/docs`, or use tools like:

- curl (command line)
- Postman
- HTTPie
- Your browser (for GET requests)

### Updating Dependencies

To update dependencies:

```bash
pip install --upgrade -r requirements.txt
pip freeze > requirements.txt
```

## Troubleshooting

### Port Already in Use

If port 8000 is already in use, specify a different port:

```bash
uvicorn main:app --reload --port 8001
```

### CSV File Not Found

Ensure `Qlik Sense Port Pairs SpotOn.csv` is in the same directory as `main.py`.

### Virtual Environment Issues

If you have issues with the virtual environment:

```bash
deactivate  # if currently activated
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## License

Internal use for CMA CGM data analysis.

## Support

For issues or questions, contact the development team.
