# Port to City Endpoint

## Overview

The `/port-to-city` endpoint converts UN/LOCODE port codes to their corresponding city names.

**Smart Response Format:**

- Single port input → Returns a **string** (just the city name)
- Multiple ports input → Returns an **array of strings** (city names)

**Flexible Input Formats:**

- Single string: `ports=NOBGO`
- JSON array: `ports=["NOBGO","CNYTN","NLRTM"]`
- Multiple params: `ports=NOBGO&ports=CNYTN&ports=NLRTM`

## Usage

### Method 1: Single Port String

```
GET /port-to-city?ports=NOBGO
```

Response:

```json
"Bergen"
```

### Method 2: JSON Array String

```
GET /port-to-city?ports=["NOBGO","CNYTN","NLRTM","USNYC"]
```

Response:

```json
["Bergen", "Yantian", "Rotterdam", "New York"]
```

### Method 3: Multiple Query Parameters

```
GET /port-to-city?ports=NOBGO&ports=CNYTN&ports=NLRTM&ports=USNYC
```

Response:

```json
["Bergen", "Yantian", "Rotterdam", "New York"]
```

### Unknown Port Code

**Single:**

```
GET /port-to-city?ports=XXXXX
```

Response:

```json
"Unknown"
```

**Multiple:**

```
GET /port-to-city?ports=["XXXXX","NOBGO"]
```

Response:

```json
["Unknown", "Bergen"]
```

### Special Case: 'none'

When you pass `ports=none` (case-insensitive), it returns an empty string:

```
GET /port-to-city?ports=none
```

Response:

```json
""
```

This is useful for handling optional port fields or placeholder values.

## Supported Ports

The endpoint includes mappings for major ports in:

- China (Shanghai, Yantian, Ningbo, etc.)
- Europe (Rotterdam, Hamburg, Antwerp, etc.)
- North America (Los Angeles, New York, Houston, etc.)
- Southeast Asia (Singapore, Hong Kong, Bangkok, etc.)
- Middle East (Jebel Ali, Jeddah, Hamad Port, etc.)
- South America (Santos, Buenos Aires, etc.)
- Africa (Durban, Mombasa, Lagos, etc.)
- Oceania (Melbourne, Sydney, Auckland, etc.)

## cURL Examples

```bash
# Single port (returns string)
curl "http://localhost:8000/port-to-city?ports=NOBGO"
# Output: "Bergen"

# JSON array (returns array of strings)
curl "http://localhost:8000/port-to-city?ports=[\"NOBGO\",\"CNYTN\",\"NLRTM\"]"
# Output: ["Bergen", "Yantian", "Rotterdam"]

# Multiple params (returns array of strings)
curl "http://localhost:8000/port-to-city?ports=NOBGO&ports=CNYTN&ports=NLRTM"
# Output: ["Bergen", "Yantian", "Rotterdam"]
```

## JavaScript/Fetch Examples

### Single Port

```javascript
const response = await fetch("/port-to-city?ports=NOBGO");
const city = await response.json();
// city = "Bergen" (string)
console.log(city); // "Bergen"
```

### JSON Array Format

```javascript
const ports = ["NOBGO", "CNYTN", "NLRTM"];
const portsJson = JSON.stringify(ports);
const response = await fetch(
  `/port-to-city?ports=${encodeURIComponent(portsJson)}`
);
const cities = await response.json();
// cities = ["Bergen", "Yantian", "Rotterdam"]
```

### Multiple Query Params

```javascript
const ports = ["NOBGO", "CNYTN", "NLRTM"];
const params = new URLSearchParams();
ports.forEach((port) => params.append("ports", port));
const response = await fetch(`/port-to-city?${params}`);
const cities = await response.json();
// cities = ["Bergen", "Yantian", "Rotterdam"]
```

## Python Examples

```python
import requests
import json

# Single port
response = requests.get("http://localhost:8000/port-to-city", params={"ports": "NOBGO"})
city = response.json()  # "Bergen"

# JSON array format
ports = ["NOBGO", "CNYTN", "NLRTM"]
response = requests.get(
    "http://localhost:8000/port-to-city",
    params={"ports": json.dumps(ports)}
)
cities = response.json()  # ["Bergen", "Yantian", "Rotterdam"]

# Multiple params format
response = requests.get(
    "http://localhost:8000/port-to-city",
    params=[("ports", "NOBGO"), ("ports", "CNYTN"), ("ports", "NLRTM")]
)
cities = response.json()  # ["Bergen", "Yantian", "Rotterdam"]
```

## Node.js/Axios Example

```javascript
const axios = require("axios");

// Single port
const city = await axios
  .get("http://localhost:8000/port-to-city", {
    params: { ports: "NOBGO" },
  })
  .then((res) => res.data);
// city = "Bergen"

// JSON array
const ports = ["NOBGO", "CNYTN", "NLRTM"];
const cities = await axios
  .get("http://localhost:8000/port-to-city", {
    params: { ports: JSON.stringify(ports) },
  })
  .then((res) => res.data);
// cities = ["Bergen", "Yantian", "Rotterdam"]
```
