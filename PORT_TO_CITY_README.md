# Port to City Endpoint

## Overview

The `/port-to-city` endpoint converts UN/LOCODE port codes to their corresponding city names.

**Smart Response Format:**

- Single port input → Returns a **string** (just the city name)
- Multiple ports input → Returns an **array of strings** (just city names)

## Usage

### Single Port Code (Returns String)

```
GET /port-to-city?ports=NOBGO
```

Response:

```json
"Bergen"
```

### Multiple Port Codes (Returns Array of Strings)

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
GET /port-to-city?ports=XXXXX&ports=NOBGO
```

Response:

```json
["Unknown", "Bergen"]
```

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

# Multiple ports (returns array of strings)
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

### Multiple Ports

```javascript
const ports = ["NOBGO", "CNYTN", "NLRTM"];
const params = new URLSearchParams();
ports.forEach((port) => params.append("ports", port));
const response = await fetch(`/port-to-city?${params}`);
const cities = await response.json();
// cities = ["Bergen", "Yantian", "Rotterdam"]
cities.forEach((city, index) => {
  console.log(`${ports[index]} -> ${city}`);
});
```

## Python Example

```python
import requests

# Single port
response = requests.get("http://localhost:8000/port-to-city", params={"ports": "NOBGO"})
city = response.json()  # "Bergen"

# Multiple ports
response = requests.get(
    "http://localhost:8000/port-to-city",
    params=[("ports", "NOBGO"), ("ports", "CNYTN"), ("ports", "NLRTM")]
)
cities = response.json()  # ["Bergen", "Yantian", "Rotterdam"]
```
