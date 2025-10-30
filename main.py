from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional, Union

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

# Port code to city name mapping (UN/LOCODE standard)
PORT_TO_CITY = {
    # China
    "CNYTN": "Yantian",
    "CNSHA": "Shanghai",
    "CNNGB": "Ningbo",
    "CNSHK": "Shekou",
    "CNTAO": "Qingdao",
    "CNTXG": "Tianjin Xingang",
    "CNXMN": "Xiamen",
    "CNDLC": "Dalian",
    "CNHUA": "Huangpu",
    "CNSZX": "Shenzhen",
    "CNQZH": "Quanzhou",
    "CNFOC": "Fuzhou",
    "CNLYG": "Lianyungang",
    "CNWUH": "Wuhan",
    "CNZUH": "Zhuhai",
    "CNZJG": "Zhanjiang",
    "CNCAN": "Guangzhou",
    "CNNKG": "Nanjing",
    "CNSHG": "Shanghai",
    # Hong Kong
    "HKHKG": "Hong Kong",
    # Singapore
    "SGSIN": "Singapore",
    # Japan
    "JPNGO": "Nagoya",
    "JPOSA": "Osaka",
    "JPTYO": "Tokyo",
    "JPYOK": "Yokohama",
    "JPUKB": "Kobe",
    "JPHKT": "Hakata",
    "JPMOJ": "Moji",
    # South Korea
    "KRPUS": "Busan",
    "KRICH": "Incheon",
    # Taiwan
    "TWKHH": "Kaohsiung",
    "TWTPE": "Taipei",
    # Southeast Asia
    "THBKK": "Bangkok",
    "THLCH": "Laem Chabang",
    "VNSGN": "Ho Chi Minh City",
    "VNHPH": "Haiphong",
    "VNDAD": "Da Nang",
    "VNVUT": "Vung Tau",
    "IDJKT": "Jakarta",
    "IDSUB": "Surabaya",
    "IDBLW": "Belawan",
    "MYBTU": "Bintulu",
    "MYPEN": "Penang",
    "MYPKG": "Port Klang",
    "MYTPP": "Tanjung Pelepas",
    "PHMNL": "Manila",
    "KHKOS": "Sihanoukville",
    # Middle East
    "AEJEA": "Jebel Ali",
    "AEAJM": "Ajman",
    "AESHJ": "Sharjah",
    "AEKHL": "Khalifa Port",
    "OMSLL": "Salalah",
    "OMSOH": "Sohar",
    "SAJED": "Jeddah",
    "QAHMD": "Hamad Port",
    "KWSWK": "Shuwaikh",
    "BHKBS": "Khalifa Bin Salman",
    "PKBQM": "Karachi",
    "PKKHI": "Karachi",
    # India
    "INNSA": "Nhava Sheva",
    "INMUN": "Mumbai",
    "INCCU": "Kolkata",
    "INCOK": "Kochi",
    "INHZA": "Hazira",
    "INVTZ": "Visakhapatnam",
    "INIXE": "Mangalore",
    "INTUT": "Tuticorin",
    # Europe
    "NLRTM": "Rotterdam",
    "DEHAM": "Hamburg",
    "BEANR": "Antwerp",
    "FRFOS": "Fos-sur-Mer",
    "FRLEH": "Le Havre",
    "GBFXT": "Felixstowe",
    "GBLGP": "London Gateway",
    "GBSOU": "Southampton",
    "ITGOA": "Genoa",
    "ITLIV": "Livorno",
    "ITNAP": "Naples",
    "ITSPE": "La Spezia",
    "ESBCN": "Barcelona",
    "ESVLC": "Valencia",
    "ESALG": "Algeciras",
    "PTLEI": "Leixoes",
    "GRPIR": "Piraeus",
    "TRIZM": "Izmir",
    "TRMER": "Mersin",
    "EGALY": "Alexandria",
    "EGPSD": "Port Said",
    "MACAS": "Casablanca",
    "DZALG": "Algiers",
    "TNTUN": "Tunis",
    "LBBEY": "Beirut",
    "ILHFA": "Haifa",
    "ILASD": "Ashdod",
    "NOKRS": "Kristiansand",
    "NOBGO": "Bergen",
    "NOOSL": "Oslo",
    "SEGOT": "Gothenburg",
    "FIHEL": "Helsinki",
    "PLGDN": "Gdansk",
    "DKCPH": "Copenhagen",
    # Africa
    "ZADUR": "Durban",
    "ZACPT": "Cape Town",
    "ZAPLZ": "Port Elizabeth",
    "KEMBA": "Mombasa",
    "TZDAR": "Dar es Salaam",
    "TZZNZ": "Zanzibar",
    "NGAPP": "Apapa",
    "NGLKK": "Lagos",
    "GHTEM": "Tema",
    "CIABJ": "Abidjan",
    "CMDLA": "Douala",
    "AOLAD": "Luanda",
    "MRNKC": "Nouakchott",
    "SNDKR": "Dakar",
    # North America
    "USLAX": "Los Angeles",
    "USLGB": "Long Beach",
    "USNYC": "New York",
    "USOAK": "Oakland",
    "USORF": "Norfolk",
    "USSAV": "Savannah",
    "USHOU": "Houston",
    "USCHS": "Charleston",
    "USMIA": "Miami",
    "USSEA": "Seattle",
    "CAVAN": "Vancouver",
    "CAMTR": "Montreal",
    "MXVER": "Veracruz",
    "MXATM": "Altamira",
    "MXLZC": "Lazaro Cardenas",
    # South America
    "BRSSZ": "Santos",
    "BRRIO": "Rio de Janeiro",
    "BRPNG": "Paranagua",
    "CLSAI": "San Antonio",
    "CLVAP": "Valparaiso",
    "PECLL": "Callao",
    "COCTG": "Cartagena",
    "COBUN": "Buenaventura",
    "ECGYE": "Guayaquil",
    "ARBUE": "Buenos Aires",
    "UYMVD": "Montevideo",
    # Oceania
    "AUMEL": "Melbourne",
    "AUSYD": "Sydney",
    "AUBNE": "Brisbane",
    "AUFRE": "Fremantle",
    "AUADL": "Adelaide",
    "NZAKL": "Auckland",
    "NZWLG": "Wellington",
}


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
            "/port-to-city": "Convert port codes to city names (string or array)",
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
        return {
            "port_pair": port_pair,
            "data": [],
            "status_code": 404,
            "detail": f"Port pair '{port_pair}' not found. Use /port-pairs to see available port pairs.",
        }
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


@app.get("/port-to-city")
async def port_to_city(
    ports: Union[str, List[str]] = Query(
        ...,
        description="Port code(s) - single string 'CNYTN' or array ['CNYTN','NLRTM'] or multiple params",
    )
):
    """
    Convert port code(s) to city name(s).

    Accepts either:
    - Single port code (string): /port-to-city?ports=CNYTN
      Returns: "Yantian"

    - Multiple port codes (array, JSON format): /port-to-city?ports=["CNYTN","NLRTM","USNYC"]
      Returns: ["Yantian", "Rotterdam", "New York"]

    - Multiple port codes (repeated params): /port-to-city?ports=CNYTN&ports=NLRTM&ports=USNYC
      Returns: ["Yantian", "Rotterdam", "New York"]

    - Special case 'none': /port-to-city?ports=none
      Returns: "" (empty string)

    If a single string is provided, returns just the city name as a string.
    If multiple values are provided (array), returns an array of city names (strings).
    Unknown ports will return "Unknown".
    Special value "none" (case-insensitive) returns an empty string.

    Examples:
    - /port-to-city?ports=CNYTN
      Returns: "Yantian"

    - /port-to-city?ports=["CNYTN","NLRTM","NOBGO"]
      Returns: ["Yantian", "Rotterdam", "Bergen"]

    - /port-to-city?ports=CNYTN&ports=NLRTM&ports=NOBGO
      Returns: ["Yantian", "Rotterdam", "Bergen"]

    - /port-to-city?ports=none
      Returns: ""
    """

    # Handle special case: 'none' returns empty string
    if isinstance(ports, str) and ports.lower() == "none":
        return ""

    # Handle different input formats
    port_list = []

    if isinstance(ports, str):
        # Check if it's a JSON array string
        if ports.startswith("[") and ports.endswith("]"):
            try:
                # Parse JSON array
                port_list = json.loads(ports)
                if not isinstance(port_list, list):
                    port_list = [ports]
            except json.JSONDecodeError:
                # If parsing fails, treat as single port
                port_list = [ports]
        else:
            # Single port string
            port_list = [ports]
    else:
        # Already a list (from multiple query params)
        port_list = ports

    # Process the ports
    if len(port_list) == 1:
        # Single port - return just the city name as a string
        port_upper = port_list[0].strip().upper()
        return PORT_TO_CITY.get(port_upper, "Unknown")
    else:
        # Multiple ports - return array of city names
        result = []
        for port_code in port_list:
            port_upper = port_code.strip().upper()
            if port_upper:  # Skip empty strings
                result.append(PORT_TO_CITY.get(port_upper, "Unknown"))
        return result


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
