from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
from pathlib import Path
from typing import Dict, List

# Initialize FastAPI app
app = FastAPI(
    title="Port Pairs SpotOn API",
    description="API to query port pair booking data from CMA CGM SpotOn",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable to store the dataframe
df = None


def load_data():
    """Load the CSV data on startup"""
    global df
    try:
        # Get the directory where this script is located
        base_dir = Path(__file__).resolve().parent
        csv_path = base_dir / "Qlik Sense Port Pairs SpotOn.csv"

        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found at {csv_path}")

        df = pd.read_csv(
            csv_path,
            skiprows=1,
            delimiter=";",
            index_col="POL-POD Booked",
        )
        print(f"✓ Data loaded successfully: {len(df)} port pairs")
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        raise


@app.on_event("startup")
async def startup_event():
    """Load data when the application starts"""
    load_data()


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Port Pairs SpotOn API",
        "version": "1.0.0",
        "endpoints": {
            "/health": "Health check endpoint",
            "/port-pairs": "Get list of all available port pairs",
            "/port-pairs/{port_pair}": "Get data for a specific port pair",
            "/dates": "Get list of all available dates",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if df is None:
        raise HTTPException(
            status_code=503, detail="Service unavailable - data not loaded"
        )

    return {"status": "healthy", "data_loaded": True, "port_pairs_count": len(df)}


@app.get("/port-pairs")
async def get_all_port_pairs() -> List[str]:
    """Get list of all available port pairs"""
    if df is None:
        raise HTTPException(
            status_code=503, detail="Service unavailable - data not loaded"
        )

    return df.index.tolist()


@app.get("/port-pairs/{port_pair}")
async def get_port_pair_data(port_pair: str):
    """
    Get booking data for a specific port pair.

    Example: /port-pairs/BJCOO-BRPEC
    """
    if df is None:
        raise HTTPException(
            status_code=503, detail="Service unavailable - data not loaded"
        )

    try:
        # Try to get the data for the port pair
        data = df.loc[port_pair]

        # Convert to dict and handle the response
        result = {"port_pair": port_pair, "data": data.to_dict()}

        return result
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Port pair '{port_pair}' not found. Use /port-pairs to see available port pairs.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/dates")
async def get_dates() -> List[str]:
    """Get list of all available dates (column names)"""
    if df is None:
        raise HTTPException(
            status_code=503, detail="Service unavailable - data not loaded"
        )

    return df.columns.tolist()


@app.get("/search")
async def search_port_pairs(origin: str = None, destination: str = None):
    """
    Search port pairs by origin and/or destination code.

    Example: /search?origin=CIABJ or /search?destination=BRPEC
    """
    if df is None:
        raise HTTPException(
            status_code=503, detail="Service unavailable - data not loaded"
        )

    if not origin and not destination:
        raise HTTPException(
            status_code=400,
            detail="Please provide at least one of 'origin' or 'destination' parameter",
        )

    port_pairs = df.index.tolist()
    filtered_pairs = []

    for pair in port_pairs:
        parts = pair.split("-")
        if len(parts) == 2:
            pol, pod = parts
            match = True
            if origin and origin.upper() not in pol.upper():
                match = False
            if destination and destination.upper() not in pod.upper():
                match = False
            if match:
                filtered_pairs.append(pair)

    return {
        "query": {"origin": origin, "destination": destination},
        "results": filtered_pairs,
        "count": len(filtered_pairs),
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
