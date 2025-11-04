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
# Expanded from UN/LOCODE 2024-2 database with 511 port locations worldwide
# All port codes are without spaces as per standard usage
PORT_TO_CITY = {
    # United Arab Emirates
    "AEAJM": "Ajman",
    "AEAUH": "Abu Dhabi",
    "AEDXB": "Dubai",
    "AEFUJ": "Fujairah",
    "AEJEA": "Jebel Ali",
    "AEKHL": "Khalifa Port",
    "AESHJ": "Sharjah",
    # Angola
    "AOLAD": "Luanda",
    "AOLOB": "Lobito",
    # Argentina
    "ARBHI": "Bahia Blanca",
    "ARBUE": "Buenos Aires",
    "ARROS": "Rosario",
    "ARZAE": "Zarate",
    # Australia
    "AUADL": "Adelaide",
    "AUBNE": "Brisbane",
    "AUDPO": "Darwin",
    "AUFRE": "Fremantle",
    "AUMEL": "Melbourne",
    "AUNCL": "Newcastle",
    "AUPER": "Perth",
    "AUPTL": "Port Lincoln",
    "AUSYD": "Sydney",
    "AUTOW": "Townsville",
    # Aruba
    "AWAUA": "Aruba",
    # Barbados
    "BBBGI": "Bridgetown",
    # Bangladesh
    "BDCGP": "Chittagong",
    "BDDAC": "Dhaka",
    # Belgium
    "BEANR": "Antwerp",
    "BEBRU": "Brussels",
    "BEOST": "Oostende",
    "BEZEE": "Zeebrugge",
    # Bahrain
    "BHBAH": "Bahrain",
    "BHKBS": "Khalifa Bin Salman",
    # Benin
    "BJCOO": "Cotonou",
    # Bermuda
    "BMBDA": "Bermuda",
    # Bolivia
    "BOLVB": "La Paz",
    # Brazil
    "BRBEL": "Belem",
    "BRFOR": "Fortaleza",
    "BRGRU": "Guaruja",
    "BRIGU": "Iguassu",
    "BRITJ": "Itajai",
    "BRMAO": "Manaus",
    "BRPNG": "Paranagua",
    "BRREC": "Recife",
    "BRRIO": "Rio de Janeiro",
    "BRSFS": "Sao Francisco do Sul",
    "BRSJP": "Sao Jose dos Pinhais",
    "BRSSA": "Salvador",
    "BRSSZ": "Santos",
    "BRSUA": "Suape",
    "BRVDC": "Vitoria",
    # Bahamas
    "BSFPO": "Freeport",
    "BSNAS": "Nassau",
    # Canada
    "CAHAL": "Halifax",
    "CAMTR": "Montreal",
    "CAPRI": "Prince Rupert",
    "CAQBC": "Quebec",
    "CASJS": "Saint John",
    "CATOR": "Toronto",
    "CAVAN": "Vancouver",
    "CAVIC": "Victoria",
    # Congo
    "CGPNR": "Pointe Noire",
    # Ivory Coast
    "CIABJ": "Abidjan",
    "CIVRR": "San Pedro",
    # Chile
    "CLARI": "Arica",
    "CLIQQ": "Iquique",
    "CLLQN": "Lirquen",
    "CLSAI": "San Antonio",
    "CLSCL": "Santiago",
    "CLTCO": "Talcahuano",
    "CLVAP": "Valparaiso",
    # Cameroon
    "CMDLA": "Douala",
    "CMYAO": "Yaounde",
    # China
    "CNBHZ": "Beihai",
    "CNCAN": "Guangzhou",
    "CNCHI": "Chiwan",
    "CNDLC": "Dalian",
    "CNDOC": "Dongguan",
    "CNFOC": "Fuzhou",
    "CNHAK": "Haikou",
    "CNHUA": "Huangpu",
    "CNHUI": "Huizhou",
    "CNJIA": "Jiangmen",
    "CNJIN": "Jinzhou",
    "CNJIU": "Jiujiang",
    "CNLIU": "Liuheng",
    "CNLYG": "Lianyungang",
    "CNNAN": "Nansha",
    "CNNGB": "Ningbo",
    "CNNKG": "Nanjing",
    "CNQZH": "Quanzhou",
    "CNSHA": "Shanghai",
    "CNSHG": "Shanghai",
    "CNSHK": "Shekou",
    "CNSWA": "Shantou",
    "CNSZX": "Shenzhen",
    "CNTAI": "Taicang",
    "CNTAO": "Qingdao",
    "CNTXG": "Tianjin Xingang",
    "CNWEI": "Weihai",
    "CNWUH": "Wuhan",
    "CNXMN": "Xiamen",
    "CNYAN": "Yantai",
    "CNYTN": "Yantian",
    "CNZHA": "Zhapu",
    "CNZHZ": "Zhenjiang",
    "CNZJG": "Zhanjiang",
    "CNZUH": "Zhuhai",
    # Colombia
    "COBAQ": "Barranquilla",
    "COBOG": "Bogota",
    "COBUN": "Buenaventura",
    "COCTG": "Cartagena",
    "COSTR": "Santa Marta",
    # Costa Rica
    "CRCLD": "Caldera",
    "CRLIM": "Puerto Limon",
    "CRSJO": "San Jose",
    # Cuba
    "CUHAV": "Havana",
    "CUMOA": "Moa",
    # Curacao
    "CWWIL": "Willemstad",
    # Cyprus
    "CYLMS": "Limassol",
    "CYNIC": "Nicosia",
    # Germany
    "DEBRE": "Bremen",
    "DEBRV": "Bremerhaven",
    "DEEMB": "Emden",
    "DEHAM": "Hamburg",
    "DEKEL": "Kiel",
    "DELBC": "Lubeck",
    "DEROS": "Rostock",
    "DEWVN": "Wilhelmshaven",
    # Djibouti
    "DJJIB": "Djibouti",
    # Denmark
    "DKAAR": "Aarhus",
    "DKCPH": "Copenhagen",
    # Dominican Republic
    "DOCAU": "Caucedo",
    "DOSDQ": "Santo Domingo",
    # Algeria
    "DZAAE": "Annaba",
    "DZALG": "Algiers",
    "DZORN": "Oran",
    # Ecuador
    "ECGYE": "Guayaquil",
    "ECMEC": "Manta",
    "ECUIO": "Quito",
    # Estonia
    "EETLL": "Tallinn",
    # Egypt
    "EGALY": "Alexandria",
    "EGCAI": "Cairo",
    "EGDAM": "Damietta",
    "EGPSD": "Port Said",
    "EGSOK": "Sokhna",
    # Spain
    "ESALG": "Algeciras",
    "ESBCN": "Barcelona",
    "ESBIO": "Bilbao",
    "ESLPA": "Las Palmas",
    "ESMAD": "Madrid",
    "ESMAL": "Malaga",
    "ESSCQ": "Santiago de Compostela",
    "ESSVQ": "Seville",
    "ESVLC": "Valencia",
    # Ethiopia
    "ETADD": "Addis Ababa",
    # Finland
    "FIHAM": "Hamina",
    "FIHEL": "Helsinki",
    "FIKTK": "Kotka",
    "FITUR": "Turku",
    # Fiji
    "FJSUV": "Suva",
    # Faroe Islands
    "FOTHO": "Torshavn",
    # France
    "FRBAY": "Bayonne",
    "FRBOD": "Bordeaux",
    "FRDKK": "Dunkirk",
    "FRFOS": "Fos-sur-Mer",
    "FRLEH": "Le Havre",
    "FRLYO": "Lyon",
    "FRMRS": "Marseille",
    "FRNTE": "Nantes",
    "FRPAR": "Paris",
    "FRSRG": "Strasbourg",
    # Gabon
    "GALIB": "Libreville",
    "GAPOG": "Port Gentil",
    # United Kingdom
    "GBBEL": "Belfast",
    "GBFXT": "Felixstowe",
    "GBGRG": "Grangemouth",
    "GBHUL": "Hull",
    "GBLGP": "London Gateway",
    "GBLIV": "Liverpool",
    "GBLON": "London",
    "GBSOU": "Southampton",
    "GBTHP": "Thamesport",
    "GBTIL": "Tilbury",
    # French Guiana
    "GFCAY": "Cayenne",
    # Ghana
    "GHACC": "Accra",
    "GHTEM": "Tema",
    # Greenland
    "GLGOH": "Nuuk",
    # Gambia
    "GMBJL": "Banjul",
    # Guinea
    "GNCKR": "Conakry",
    # Greece
    "GRATH": "Athens",
    "GRHER": "Heraklion",
    "GRPIR": "Piraeus",
    "GRTHE": "Thessaloniki",
    # Guatemala
    "GTGUA": "Guatemala City",
    "GTQUE": "Quetzal",
    # Guam
    "GUGUM": "Guam",
    # Guyana
    "GYGEO": "Georgetown",
    # Hong Kong
    "HKHKG": "Hong Kong",
    # Honduras
    "HNPCO": "Puerto Cortes",
    "HNTGU": "Tegucigalpa",
    # Croatia
    "HRRJK": "Rijeka",
    "HRZAG": "Zagreb",
    # Indonesia
    "IDBDJ": "Banjarmasin",
    "IDBLW": "Belawan",
    "IDBPN": "Balikpapan",
    "IDBTM": "Batam",
    "IDJKT": "Jakarta",
    "IDMKS": "Makassar",
    "IDPDK": "Padang",
    "IDPLG": "Palembang",
    "IDPNK": "Pontianak",
    "IDSRG": "Semarang",
    "IDSUB": "Surabaya",
    "IDTPP": "Tanjung Priok",
    # Ireland
    "IECORK": "Cork",
    "IEDUB": "Dublin",
    # Israel
    "ILASD": "Ashdod",
    "ILETH": "Eilat",
    "ILHFA": "Haifa",
    "ILTLV": "Tel Aviv",
    # India
    "INAHD": "Ahmedabad",
    "INBLR": "Bangalore",
    "INCCU": "Kolkata",
    "INCHE": "Chennai",
    "INCOK": "Kochi",
    "INDEL": "Delhi",
    "INHYD": "Hyderabad",
    "INHZA": "Hazira",
    "INIXE": "Mangalore",
    "INJAI": "Jaipur",
    "INKAN": "Kandla",
    "INKNU": "Kanpur",
    "INMUN": "Mumbai",
    "INMUN1": "Mundra",
    "INNSA": "Nhava Sheva",
    "INPAV": "Pipavav",
    "INPUN": "Pune",
    "INSUR": "Surat",
    "INTUT": "Tuticorin",
    "INVTZ": "Visakhapatnam",
    # Iraq
    "IQBGW": "Baghdad",
    "IQBSR": "Basra",
    "IQUMQ": "Umm Qasr",
    # Iran
    "IRBND": "Bandar Abbas",
    "IRBUX": "Bushehr",
    "IRKHO": "Khorramshahr",
    "IRTHR": "Tehran",
    # Iceland
    "ISREY": "Reykjavik",
    # Italy
    "ITGIT": "Gioia Tauro",
    "ITGOA": "Genoa",
    "ITLIV": "Livorno",
    "ITMIL": "Milan",
    "ITNAP": "Naples",
    "ITROM": "Rome",
    "ITSAL": "Salerno",
    "ITSPE": "La Spezia",
    "ITTRN": "Trieste",
    "ITTRS": "Taranto",
    "ITVCE": "Venice",
    # Jamaica
    "JMKIN": "Kingston",
    "JMMBT": "Montego Bay",
    # Jordan
    "JOAMM": "Amman",
    "JOAQJ": "Aqaba",
    # Japan
    "JPCHI": "Chiba",
    "JPFUK": "Fukuoka",
    "JPHIJ": "Hiroshima",
    "JPHKT": "Hakata",
    "JPKAN": "Kanazawa",
    "JPKIT": "Kitakyushu",
    "JPKSZ": "Shimizu",
    "JPMOJ": "Moji",
    "JPNAH": "Naha",
    "JPNGO": "Nagoya",
    "JPNIS": "Niigata",
    "JPOKA": "Okinawa",
    "JPOSA": "Osaka",
    "JPSZE": "Sendai",
    "JPTOY": "Toyama",
    "JPTYO": "Tokyo",
    "JPUKB": "Kobe",
    "JPYOK": "Yokohama",
    # Kenya
    "KEMBA": "Mombasa",
    "KENBO": "Nairobi",
    # Cambodia
    "KHKOS": "Sihanoukville",
    "KHPNH": "Phnom Penh",
    # South Korea
    "KRICH": "Incheon",
    "KRKWN": "Gwangyang",
    "KRMKP": "Mokpo",
    "KRPTK": "Pyeongtaek",
    "KRPUS": "Busan",
    "KRSUW": "Suwon",
    "KRULS": "Ulsan",
    # Kuwait
    "KWKWI": "Kuwait City",
    "KWSWK": "Shuwaikh",
    # Cayman Islands
    "KYGEC": "Grand Cayman",
    # Lebanon
    "LBBEY": "Beirut",
    "LBTYR": "Tyre",
    # Sri Lanka
    "LKCMB": "Colombo",
    "LKGAL": "Galle",
    # Liberia
    "LRMLW": "Monrovia",
    # Lithuania
    "LTKLJ": "Klaipeda",
    "LTVNO": "Vilnius",
    # Latvia
    "LVRIX": "Riga",
    "LVVEN": "Ventspils",
    # Libya
    "LYBEN": "Benghazi",
    "LYTIP": "Tripoli",
    # Morocco
    "MAAGG": "Agadir",
    "MACAS": "Casablanca",
    "MARAB": "Rabat",
    "MATNG": "Tangier",
    # Madagascar
    "MGTMY": "Antananarivo",
    "MGTNR": "Toamasina",
    # Myanmar
    "MMMDY": "Mandalay",
    "MMRGN": "Yangon",
    # Macau
    "MOMFM": "Macau",
    # Mauritania
    "MRNKC": "Nouakchott",
    # Malta
    "MTMLA": "Marsaxlokk",
    "MTVAL": "Valletta",
    # Mauritius
    "MUPLU": "Port Louis",
    # Mexico
    "MXATM": "Altamira",
    "MXLZC": "Lazaro Cardenas",
    "MXMAN": "Manzanillo",
    "MXMEX": "Mexico City",
    "MXPVM": "Progreso",
    "MXSZA": "Salina Cruz",
    "MXTAM": "Tampico",
    "MXVER": "Veracruz",
    "MXZLO": "Manzanillo Colima",
    # Malaysia
    "MYBTU": "Bintulu",
    "MYJHB": "Johor Bahru",
    "MYKCH": "Kuching",
    "MYKUA": "Kuantan",
    "MYKUL": "Kuala Lumpur",
    "MYLDU": "Lahad Datu",
    "MYMTW": "Miri",
    "MYPEN": "Penang",
    "MYPKG": "Port Klang",
    "MYSBW": "Sibu",
    "MYTPP": "Tanjung Pelepas",
    # Mozambique
    "MZBEW": "Beira",
    "MZMPM": "Maputo",
    # Namibia
    "NAWDH": "Walvis Bay",
    "NAWVB": "Windhoek",
    # New Caledonia
    "NCNOU": "Noumea",
    # Nigeria
    "NGAPP": "Apapa",
    "NGLKK": "Lagos",
    "NGPHC": "Port Harcourt",
    "NGTIN": "Tin Can Island",
    # Nicaragua
    "NICOR": "Corinto",
    "NIMGA": "Managua",
    # Netherlands
    "NLAMS": "Amsterdam",
    "NLMOE": "Moerdijk",
    "NLRTM": "Rotterdam",
    "NLVLI": "Vlissingen",
    # Norway
    "NOBGO": "Bergen",
    "NOKRS": "Kristiansand",
    "NOOSL": "Oslo",
    "NOSVG": "Stavanger",
    "NOTRD": "Trondheim",
    # New Zealand
    "NZAKL": "Auckland",
    "NZCHC": "Christchurch",
    "NZLYT": "Lyttelton",
    "NZTRG": "Tauranga",
    "NZWLG": "Wellington",
    # Oman
    "OMMCT": "Muscat",
    "OMSLL": "Salalah",
    "OMSOH": "Sohar",
    "OMSUZ": "Suwaiq",
    # Panama
    "PABAL": "Balboa",
    "PACTB": "Cristobal",
    "PAMIT": "Manzanillo International Terminal",
    "PAPAC": "Panama City",
    # Peru
    "PECLL": "Callao",
    "PELIM": "Lima",
    "PEPAI": "Paita",
    # French Polynesia
    "PFPPT": "Papeete",
    # Papua New Guinea
    "PGLAE": "Lae",
    "PGPOM": "Port Moresby",
    # Philippines
    "PHBCD": "Bacolod",
    "PHCEB": "Cebu",
    "PHCGY": "Cagayan de Oro",
    "PHDVO": "Davao",
    "PHILO": "Iloilo",
    "PHMNL": "Manila",
    "PHSBX": "Subic Bay",
    "PHZAM": "Zamboanga",
    # Pakistan
    "PKBQM": "Karachi",
    "PKGWD": "Gwadar",
    "PKISB": "Islamabad",
    "PKKHI": "Karachi",
    "PKLHE": "Lahore",
    # Poland
    "PLGDN": "Gdansk",
    "PLGDY": "Gdynia",
    "PLSZZ": "Szczecin",
    "PLWAW": "Warsaw",
    # Puerto Rico
    "PRPON": "Ponce",
    "PRSJU": "San Juan",
    # Portugal
    "PTLEI": "Leixoes",
    "PTLIS": "Lisbon",
    "PTOPO": "Porto",
    "PTSET": "Setubal",
    "PTSIE": "Sines",
    # Paraguay
    "PYASU": "Asuncion",
    # Qatar
    "QADOH": "Doha",
    "QAHMD": "Hamad Port",
    # Reunion
    "RERUN": "Reunion",
    # Russia
    "RUKLT": "Kaliningrad",
    "RULED": "St Petersburg",
    "RUMOW": "Moscow",
    "RUMUR": "Murmansk",
    "RUNUS": "Novorossiysk",
    "RUULU": "Ulyanovsk",
    "RUVVO": "Vladivostok",
    # Saudi Arabia
    "SADMM": "Dammam",
    "SAJED": "Jeddah",
    "SAJUB": "Jubail",
    "SARAJB": "King Abdullah Port",
    "SARIY": "Riyadh",
    "SARUH": "Ras Al Khair",
    # Solomon Islands
    "SBHIR": "Honiara",
    # Seychelles
    "SCMAW": "Mahe",
    # Sweden
    "SEGOT": "Gothenburg",
    "SEHEL": "Helsingborg",
    "SEMAL": "Malmo",
    "SESTO": "Stockholm",
    # Singapore
    "SGSIN": "Singapore",
    # Slovenia
    "SIKOP": "Koper",
    "SILJU": "Ljubljana",
    # Sierra Leone
    "SLFNA": "Freetown",
    # Senegal
    "SNDKR": "Dakar",
    # Somalia
    "SOMGQ": "Mogadishu",
    # Suriname
    "SRPBM": "Paramaribo",
    # El Salvador
    "SVAQJ": "Acajutla",
    "SVSAL": "San Salvador",
    # Syria
    "SYLAT": "Latakia",
    "SYTAR": "Tartus",
    # Togo
    "TGLFW": "Lome",
    # Thailand
    "THBKK": "Bangkok",
    "THLCH": "Laem Chabang",
    "THPHU": "Phuket",
    "THSGZ": "Songkhla",
    # Tunisia
    "TNBIZ": "Bizerte",
    "TNSFA": "Sfax",
    "TNTUN": "Tunis",
    # Turkey
    "TRALI": "Aliaga",
    "TRAMB": "Ambarli",
    "TRGEM": "Gemlik",
    "TRIST": "Istanbul",
    "TRIZM": "Izmir",
    "TRMER": "Mersin",
    # Trinidad & Tobago
    "TTPAW": "Port of Spain",
    # Taiwan
    "TWHUA": "Hualien",
    "TWKEL": "Keelung",
    "TWKHH": "Kaohsiung",
    "TWTPE": "Taipei",
    "TWTXG": "Taichung",
    # Tanzania
    "TZDAR": "Dar es Salaam",
    "TZZNZ": "Zanzibar",
    # United States
    "USATL": "Atlanta",
    "USBAL": "Baltimore",
    "USBOS": "Boston",
    "USCHI": "Chicago",
    "USCHS": "Charleston",
    "USDET": "Detroit",
    "USDFW": "Dallas",
    "USFLL": "Fort Lauderdale",
    "USHOU": "Houston",
    "USJAX": "Jacksonville",
    "USLAX": "Los Angeles",
    "USLGB": "Long Beach",
    "USMIA": "Miami",
    "USMOB": "Mobile",
    "USMSY": "New Orleans",
    "USNYC": "New York",
    "USOAK": "Oakland",
    "USORF": "Norfolk",
    "USPDX": "Portland",
    "USPHL": "Philadelphia",
    "USSAN": "San Diego",
    "USSAV": "Savannah",
    "USSEA": "Seattle",
    "USSFO": "San Francisco",
    "USTAC": "Tacoma",
    "USTPA": "Tampa",
    "USWIL": "Wilmington",
    # Uruguay
    "UYMVD": "Montevideo",
    # Venezuela
    "VECCS": "Caracas",
    "VELGR": "La Guaira",
    "VEMCB": "Maracaibo",
    "VEPBL": "Puerto Cabello",
    # British Virgin Islands
    "VGTOV": "Tortola",
    # US Virgin Islands
    "VISTT": "St Thomas",
    # Vietnam
    "VNCAN": "Can Tho",
    "VNDAD": "Da Nang",
    "VNHAN": "Hanoi",
    "VNHPH": "Haiphong",
    "VNHUI": "Hue",
    "VNNHA": "Nha Trang",
    "VNQNI": "Qui Nhon",
    "VNSGN": "Ho Chi Minh City",
    "VNVUT": "Vung Tau",
    # Vanuatu
    "VUVLI": "Port Vila",
    # Samoa
    "WSAPW": "Apia",
    # Yemen
    "YEADE": "Aden",
    "YEHOD": "Hodeidah",
    # South Africa
    "ZACPT": "Cape Town",
    "ZADUR": "Durban",
    "ZAELS": "East London",
    "ZAJNB": "Johannesburg",
    "ZANGQ": "Ngqura",
    "ZAPLZ": "Port Elizabeth",
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
        return {"cities": ""}

    # Handle different input formats
    port_list = []

    print(f"DEBUG - Received ports: {ports}")
    print(f"DEBUG - Type: {type(ports)}")

    if isinstance(ports, str):
        # Check if it's a JSON array string
        if ports.startswith("[") and ports.endswith("]"):
            print(f"DEBUG - Detected JSON array string")
            try:
                # Parse JSON array
                port_list = json.loads(ports)
                print(f"DEBUG - Successfully parsed: {port_list}")
                if not isinstance(port_list, list):
                    port_list = [ports]
            except json.JSONDecodeError as e:
                # If parsing fails, treat as single port
                print(f"DEBUG - JSON parsing failed: {e}")
                port_list = [ports]
        else:
            # Single port string
            print(f"DEBUG - Single port string")
            port_list = [ports]
    else:
        # Already a list (from multiple query params or FastAPI parsing)
        print(f"DEBUG - Already a list")
        # Check if it's a list with one element that's a JSON string
        if (
            len(ports) == 1
            and isinstance(ports[0], str)
            and ports[0].startswith("[")
            and ports[0].endswith("]")
        ):
            print(f"DEBUG - List contains one JSON string element, parsing it")
            try:
                port_list = json.loads(ports[0])
                print(f"DEBUG - Successfully parsed from list element: {port_list}")
            except json.JSONDecodeError as e:
                print(f"DEBUG - JSON parsing from list element failed: {e}")
                port_list = ports
        else:
            port_list = ports

    print(f"DEBUG - Final port_list: {port_list}, length: {len(port_list)}")

    # Process the ports
    if len(port_list) == 1:
        # Single port - return just the city name as a string
        port_upper = port_list[0].strip().upper()
        return {"cities": PORT_TO_CITY.get(port_upper, "")}
    else:
        # Multiple ports - return array of city names
        result = []
        for port_code in port_list:
            port_upper = port_code.strip().upper()
            if port_upper:  # Skip empty strings
                result.append(PORT_TO_CITY.get(port_upper, ""))
        print(result)
        return {"cities": result}


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
    Proxy endpoint to query CMA CGM SpotOn API with automatic pagination.

    Makes POST requests to the CMA CGM API and aggregates all results in parallel.
    If there are multiple pages of results, fetches them concurrently for better performance.

    Example:
    /proxy?portOfLoading=ESBIO&portOfDischarge=BRSSZ&departureDate=2025-11-15&requestedEquipments=[{"numberOfContainers":5,"weightPerContainer":18000,"equipmentGroupIsoCode":"40GP"}]
    """
    import concurrent.futures
    import time

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

    url = "https://apis.cma-cgm.net/pricing/commercial/instantquote/v2/spotOn/search"
    params = {"behalfOf": "API0001734"}

    def make_request(range_header: str):
        """Helper function to make a single request with a specific range."""
        headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Range": range_header,
            "Content-Type": "application/json",
        }
        response = requests.post(
            url, params=params, headers=headers, json=payload, timeout=30
        )
        response.raise_for_status()
        return response

    start_time = time.time()

    try:
        # Make initial request to get first page and determine total results
        print(f"Making initial request with Range: 0-4")
        initial_response = make_request("0-4")

        all_data = initial_response.json()
        content_range = initial_response.headers.get("content-range")
        status_code = initial_response.status_code
        cma_func_explain = initial_response.headers.get("cma-func-explain")

        print(f"Initial response: status={status_code}, content-range={content_range}")

        # Check if there are more pages (status 206 = Partial Content)
        if status_code == 206 and content_range:
            # Parse content-range header: "0-4/15" means items 0-4 out of 15 total
            parts = content_range.split("/")
            if len(parts) == 2:
                total_items = int(parts[1])
                current_end = int(parts[0].split("-")[1])

                print(f"Total items: {total_items}, got up to: {current_end}")

                # Calculate remaining ranges to fetch (5 items per request)
                remaining_ranges = []
                start = current_end + 1
                while start < total_items:
                    end = min(
                        start + 4, total_items - 1
                    )  # Max 5 items per request (0-4)
                    remaining_ranges.append(f"{start}-{end}")
                    start = end + 1

                print(
                    f"Need to fetch {len(remaining_ranges)} more pages: {remaining_ranges}"
                )

                # Fetch remaining pages in parallel
                if remaining_ranges:
                    with concurrent.futures.ThreadPoolExecutor(
                        max_workers=5
                    ) as executor:
                        future_to_range = {
                            executor.submit(make_request, range_header): range_header
                            for range_header in remaining_ranges
                        }

                        for future in concurrent.futures.as_completed(future_to_range):
                            range_header = future_to_range[future]
                            try:
                                response = future.result()
                                page_data = response.json()
                                all_data.extend(page_data)
                                print(
                                    f"Fetched range {range_header}: {len(page_data)} items"
                                )
                            except Exception as e:
                                print(f"Error fetching range {range_header}: {e}")
                                raise

        elapsed_time = time.time() - start_time
        print(
            f"Total aggregation time: {elapsed_time:.2f}s, Total items: {len(all_data)}"
        )

        # Return aggregated results with metadata
        return {
            "data": all_data,
            "metadata": {
                "total_items": len(all_data),
                "aggregation_time_seconds": round(elapsed_time, 2),
                "initial_content_range": content_range,
                "cma_func_explain": cma_func_explain,
                "status": "complete",
            },
        }

    except requests.exceptions.HTTPError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"CMA CGM API error: {e.response.text}",
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
