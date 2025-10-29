from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional

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
            "/search": "Search port pairs by origin and/or destination",
            "/proxy": "Proxy to CMA CGM SpotOn API for live quotes",
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

    Returns empty data array if port pair not found.
    """
    if df is None:
        raise HTTPException(
            status_code=503, detail="Service unavailable - data not loaded"
        )

    try:
        # Try to get the data for the port pair
        data = df.loc[port_pair]

        # Convert to array of dictionaries in column order (already chronological)
        data_array = []
        for date in data.index:
            data_array.append({date: data[date]})

        result = {"port_pair": port_pair, "data": data_array}

        return result
    except KeyError:
        # Return empty data instead of raising error
        return {"port_pair": port_pair, 
                "data": [],  
                status_code=404, 
                detail=f"Port pair '{port_pair}' not found. Use /port-pairs to see available port pairs.",}
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
        if len(parts) >= 2:
            pol = parts[0].strip()
            pod = "-".join(parts[1:]).strip()  # Handle cases with multiple dashes
            match = True
            if origin and not pol.upper().startswith(origin.upper()):
                match = False
            if destination and not pod.upper().startswith(destination.upper()):
                match = False
            if match:
                filtered_pairs.append(pair)

    return {
        "query": {"origin": origin, "destination": destination},
        "results": filtered_pairs,
        "count": len(filtered_pairs),
    }


@app.get("/proxy")
async def proxy_spoton_request(
    portOfLoading: str = Query(..., description="Port of loading (e.g., ESBIO)"),
    portOfDischarge: str = Query(..., description="Port of discharge (e.g., BRSSZ)"),
    departureDate: str = Query(..., description="Departure date (YYYY-MM-DD)"),
    requestedEquipments: str = Query(
        ...,
        description='JSON array of equipment requests, e.g., [{"numberOfContainers":5,"weightPerContainer":18000,"equipmentGroupIsoCode":"40GP"}]',
    ),
    token: Optional[str] = Query(
        None,
        description="Optional Bearer token (if not provided, uses environment variable)",
    ),
):
    """
    Proxy endpoint to query CMA CGM SpotOn API.

    Makes a POST request to the CMA CGM API and returns the original response.

    Example:
    /proxy?portOfLoading=ESBIO&portOfDischarge=BRSSZ&departureDate=2025-11-15&requestedEquipments=[{"numberOfContainers":5,"weightPerContainer":18000,"equipmentGroupIsoCode":"40GP"}]
    """

    # Parse requestedEquipments JSON string
    try:
        equipment_list = json.loads(requestedEquipments)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid requestedEquipments format. Must be a valid JSON array.",
        )

    # Get token from parameter or environment variable
    bearer_token = token or os.environ.get("CMA_CGM_TOKEN")
    if not bearer_token:
        raise HTTPException(
            status_code=401,
            detail="No authentication token provided. Use 'token' parameter or set CMA_CGM_TOKEN environment variable.",
        )

    # Build the request payload
    payload = {
        "departureDate": departureDate,
        "portOfLoading": portOfLoading,
        "portOfDischarge": portOfDischarge,
        "locationCodificationType": "UNLOCODE",
        "spotDDSMConditionsOnly": False,
        "requestedEquipments": equipment_list,
    }

    # Make the POST request to CMA CGM API
    url = "https://apis.cma-cgm.net/pricing/commercial/instantquote/v2/spotOn/search"
    params = {"behalfOf": "API0001734"}
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Range": "0-4",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            url, params=params, headers=headers, json=payload, timeout=30
        )
        response.raise_for_status()

        # Return the original response from CMA CGM API
        return {"data": response.json()}

    except requests.exceptions.HTTPError as e:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"CMA CGM API error: {response.text}",
        )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503, detail=f"Failed to connect to CMA CGM API: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
