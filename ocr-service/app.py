from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import math

def calculate_parcel_area(geometry):
    if not geometry or geometry.get("type") != "Polygon":
        return 0.0
    coords = geometry.get("coordinates", [[]])[0]
    if len(coords) < 3:
        return 0.0
        
    # Calculate average latitude for cos factor
    sum_lat = sum(pt[1] for pt in coords)
    avg_lat = (sum_lat / len(coords)) * math.pi / 180.0
    cos_lat = math.cos(avg_lat)
    
    # Project to flat coordinates in meters
    projected = []
    for pt in coords:
        x = pt[0] * 111320.0 * cos_lat
        y = pt[1] * 110540.0
        projected.append((x, y))
        
    # Shoelace formula
    area = 0.0
    n = len(projected)
    for i in range(n):
        j = (i + 1) % n
        area += projected[i][0] * projected[j][1]
        area -= projected[j][0] * projected[i][1]
    area = abs(area) / 2.0
    
    # Convert to acres (1 acre = 4046.856 sq meters)
    acres = area / 4046.856
    return round(acres, 2)

DISTRICT_COORDS = {
    "Ludhiana": [30.9010, 75.8573],
    "Jalandhar": [31.3260, 75.5762],
    "Patiala": [30.3400, 76.3800],
    "Amritsar": [31.6340, 74.8723],
    "Bathinda": [30.2110, 74.9455],
    "Gurugram": [28.4595, 77.0266],
    "Faridabad": [28.4089, 77.3178],
    "Panipat": [29.3909, 76.9635],
    "Ambala": [30.3752, 76.7794],
    "Hisar": [29.1492, 75.7217],
    "Mumbai City": [18.9696, 72.8202],
    "Pune": [18.5204, 73.8567],
    "Nagpur": [21.1458, 79.0882],
    "Thane": [19.2183, 72.9781],
    "Nashik": [19.9975, 73.7898],
    "Bengaluru Urban": [12.9716, 77.5946],
    "Mysuru": [12.2958, 76.6394],
    "Hubballi-Dharwad": [15.3647, 75.1240],
    "Mangaluru": [12.9141, 74.8560],
    "Belagavi": [15.8497, 74.4977],
    "New Delhi": [28.6139, 77.2090],
    "North Delhi": [28.7500, 77.1500],
    "South Delhi": [28.5000, 77.2000],
    "West Delhi": [28.6500, 77.1000],
    "Lucknow": [26.8467, 80.9462],
    "Gautam Buddha Nagar (Noida)": [28.5355, 77.3910],
    "Kanpur Nagar": [26.4499, 80.3319],
    "Agra": [27.1767, 78.0081],
    "Varanasi": [25.3176, 82.9739],
    "Chennai": [13.0827, 80.2707],
    "Coimbatore": [11.0168, 76.9558],
    "Madurai": [9.9252, 78.1198],
    "Salem": [11.6643, 78.1460],
    "Trichy": [10.7905, 78.7047],
    "Ahmedabad": [23.0225, 72.5714],
    "Surat": [21.1702, 72.8311],
    "Vadodara": [22.3072, 73.1812],
    "Rajkot": [22.3039, 70.8022],
    "Gandhinagar": [23.2156, 72.6369],
    "Jaipur": [26.9124, 75.7873],
    "Jodhpur": [26.2389, 73.0243],
    "Udaipur": [24.5854, 73.7125],
    "Kota": [25.2138, 75.8648],
    "Bikaner": [28.0164, 73.3116],
    "Kolkata": [22.5726, 88.3639],
    "Howrah": [22.5735, 88.2636],
    "Darjeeling": [27.0410, 88.2627],
    "Asansol": [23.6740, 86.9521],
    "Siliguri": [26.7271, 88.3953]
}

STATE_COORDS = {
    "Punjab": [30.9010, 75.8573],
    "Haryana": [29.0588, 76.0856],
    "Maharashtra": [19.7515, 75.7139],
    "Karnataka": [15.3173, 75.7139],
    "Delhi": [28.7041, 77.1025],
    "Uttar Pradesh": [26.8467, 80.9462],
    "Tamil Nadu": [11.1271, 78.6569],
    "Gujarat": [22.2587, 71.1924],
    "Rajasthan": [27.0238, 74.2179],
    "West Bengal": [22.9868, 87.8550]
}

def get_location_coords(state, district):
    if district in DISTRICT_COORDS:
        lat, lon = DISTRICT_COORDS[district]
        offset_lat = (len(district) % 5) * 0.003 - 0.006
        offset_lon = (len(district) % 7) * 0.003 - 0.009
        return [lat + offset_lat, lon + offset_lon]
    if state in STATE_COORDS:
        return STATE_COORDS[state]
    return [26.8467, 80.9462] # default Lucknow

app = Flask(__name__)
# Enable CORS for frontend requests
CORS(app)

# 1. Centralized Mock Database
properties_db = {
    "PROP-001": {
        "id": "PROP-001",
        "propertyId": "PROP-001",
        "ownerName": "Rajesh Kumar",
        "fatherName": "Ram Lal",
        "khasra": "123/4",
        "khasraNumber": "123/4",
        "area": 2.50,
        "propertyType": "Agricultural Land",
        "state": "Uttar Pradesh",
        "district": "Lucknow",
        "tehsil": "Malihabad",
        "village": "Malihabad Rural",
        "registrationNumber": "REG-2025-0192",
        "registrationDate": "2025-06-12",
        "status": "Active Mortgage (SBI)",
        "mortgage": "State Bank of India",
        "mortgageAmount": "18,50,000",
        "mortgageDate": "15/08/2024",
        "courtCase": "None",
        "coordinates": [26.92046, 80.7105],
        "latitude": 26.92046,
        "longitude": 80.7105,
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [ [80.7100, 26.9200], [80.7110, 26.9200], [80.7110, 26.92092], [80.7100, 26.92092], [80.7100, 26.9200] ]
            ]
        },
        "address": "Malihabad Rural, Malihabad, Lucknow, Uttar Pradesh",
        "source": "SETU Demonstration Dataset",
        "sourceType": "DEMO_DATA"
    },
    "PROP-002": {
        "id": "PROP-002",
        "propertyId": "PROP-002",
        "ownerName": "Amit Sharma",
        "fatherName": "Som Nath",
        "khasra": "123/5",
        "khasraNumber": "123/5",
        "area": 1.80,
        "propertyType": "Residential Plot",
        "state": "Uttar Pradesh",
        "district": "Lucknow",
        "tehsil": "Malihabad",
        "village": "Malihabad Rural",
        "registrationNumber": "REG-2025-0456",
        "registrationDate": "2025-08-20",
        "status": "Clear",
        "mortgage": "None",
        "courtCase": "None",
        "coordinates": [26.92046, 80.7114],
        "latitude": 26.92046,
        "longitude": 80.7114,
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [ [80.7110, 26.9200], [80.71173, 26.9200], [80.71173, 26.92092], [80.7110, 26.92092], [80.7110, 26.9200] ]
            ]
        },
        "address": "Malihabad Rural, Malihabad, Lucknow, Uttar Pradesh",
        "source": "SETU Demonstration Dataset",
        "sourceType": "DEMO_DATA"
    },
    "PROP-003": {
        "id": "PROP-003",
        "propertyId": "PROP-003",
        "ownerName": "Sunita Devi",
        "fatherName": "Jagdish Prasad",
        "khasra": "123/6",
        "khasraNumber": "123/6",
        "area": 3.20,
        "propertyType": "Commercial Land",
        "state": "Uttar Pradesh",
        "district": "Lucknow",
        "tehsil": "Malihabad",
        "village": "Malihabad Rural",
        "registrationNumber": "REG-2025-0789",
        "registrationDate": "2025-04-15",
        "status": "Active Mortgage (HDFC)",
        "mortgage": "HDFC Bank",
        "mortgageAmount": "25,00,000",
        "mortgageDate": "10/01/2025",
        "courtCase": {
            "caseId": "CIV/2025/0789",
            "court": "Lucknow District Court",
            "status": "Pending",
            "issue": "Ownership dispute among siblings"
        },
        "coordinates": [26.92046, 80.71235],
        "latitude": 26.92046,
        "longitude": 80.71235,
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [ [80.71173, 26.9200], [80.71302, 26.9200], [80.71302, 26.92092], [80.71173, 26.92092], [80.71173, 26.9200] ]
            ]
        },
        "address": "Malihabad Rural, Malihabad, Lucknow, Uttar Pradesh",
        "source": "SETU Demonstration Dataset",
        "sourceType": "DEMO_DATA"
    },
    "PROP-004": {
        "id": "PROP-004",
        "propertyId": "PROP-004",
        "ownerName": "Mohan Singh",
        "fatherName": "Gurnam Singh",
        "khasra": "124/1",
        "khasraNumber": "124/1",
        "area": 1.20,
        "propertyType": "Agricultural Land",
        "state": "Uttar Pradesh",
        "district": "Lucknow",
        "tehsil": "Malihabad",
        "village": "Malihabad Rural",
        "registrationNumber": "REG-2025-0222",
        "registrationDate": "2025-03-10",
        "status": "Clear",
        "mortgage": "None",
        "courtCase": "None",
        "coordinates": [26.92135, 80.71025],
        "latitude": 26.92135,
        "longitude": 80.71025,
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [ [80.7100, 26.92092], [80.7105, 26.92092], [80.7105, 26.92178], [80.7100, 26.92178], [80.7100, 26.92092] ]
            ]
        },
        "address": "Malihabad Rural, Malihabad, Lucknow, Uttar Pradesh",
        "source": "SETU Demonstration Dataset",
        "sourceType": "DEMO_DATA"
    },
    "PROP-005": {
        "id": "PROP-005",
        "propertyId": "PROP-005",
        "ownerName": "Priya Gupta",
        "fatherName": "Ramesh Gupta",
        "khasra": "124/2",
        "khasraNumber": "124/2",
        "area": 4.10,
        "propertyType": "Industrial Plot",
        "state": "Uttar Pradesh",
        "district": "Lucknow",
        "tehsil": "Malihabad",
        "village": "Malihabad Rural",
        "registrationNumber": "REG-2025-0555",
        "registrationDate": "2025-07-05",
        "status": "Clear",
        "mortgage": "None",
        "courtCase": "None",
        "coordinates": [26.92135, 80.7113],
        "latitude": 26.92135,
        "longitude": 80.7113,
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [ [80.7105, 26.92092], [80.71216, 26.92092], [80.71216, 26.92178], [80.7105, 26.92178], [80.7105, 26.92092] ]
            ]
        },
        "address": "Malihabad Rural, Malihabad, Lucknow, Uttar Pradesh",
        "source": "SETU Demonstration Dataset",
        "sourceType": "DEMO_DATA"
    }
}

# 2. Mock Verification History
verification_history = [
    {
        "id": 1,
        "propertyId": "PROP-001",
        "ownerName": "Rajesh Kumar",
        "date": "24 Aug 2026",
        "score": 65,
        "risk": "Medium",
        "status": "Issues Found"
    },
    {
        "id": 2,
        "propertyId": "PROP-002",
        "ownerName": "Amit Sharma",
        "date": "23 Aug 2026",
        "score": 92,
        "risk": "Low",
        "status": "Verified"
    }
]

# Helper to find property by Khasra or ID
def find_property_in_db(khasra_or_id):
    khasra_or_id = khasra_or_id.strip()
    for prop_id, prop_data in properties_db.items():
        if prop_id.lower() == khasra_or_id.lower() or prop_data["khasra"] == khasra_or_id:
            return prop_data
    return None

# Endpoints
@app.route('/api/properties', methods=['GET'])
def get_properties():
    return jsonify(list(properties_db.values()))

@app.route('/api/properties/<prop_id>', methods=['GET'])
def get_property_by_id(prop_id):
    prop = properties_db.get(prop_id.upper())
    if prop:
        return jsonify(prop)
    return jsonify({"error": "Property not found"}), 404

@app.route('/api/verify/<khasra_no>', methods=['GET'])
def get_property_by_khasra(khasra_no):
    # Backward compatibility with existing endpoint
    khasra_decoded = khasra_no.replace("-", "/")
    prop = find_property_in_db(khasra_decoded)
    if prop:
        return jsonify(prop)
    
    # If not found, dynamically generate a simulated record so any search succeeds for demonstration
    owner_param = request.args.get('owner', 'Simulated Owner')
    state_param = request.args.get('state', 'Punjab')
    district_param = request.args.get('district', 'Ludhiana')
    tehsil_param = request.args.get('tehsil', 'Ludhiana West')
    village_param = request.args.get('village', 'Custom Locality')
    prop_id = request.args.get('propId') or f"PROP-{int(time.time()) % 1000:03d}"
    
    resolved_coords = get_location_coords(state_param, district_param)
    lat, lng = resolved_coords[0], resolved_coords[1]
    size = 0.0006
    dynamic_geom = {
        "type": "Polygon",
        "coordinates": [
            [
                [lng - size, lat - size],
                [lng + size, lat - size],
                [lng + size, lat + size],
                [lng - size, lat + size],
                [lng - size, lat - size]
            ]
        ]
    }

    dynamic_prop = {
        "id": prop_id,
        "propertyId": prop_id,
        "ownerName": owner_param if owner_param else "Simulated Owner",
        "fatherName": "Som Nath",
        "khasra": khasra_decoded if khasra_decoded else "100/1",
        "khasraNumber": khasra_decoded if khasra_decoded else "100/1",
        "area": 2.2,
        "propertyType": "Residential Plot",
        "location": village_param if village_param else "Custom Locality",
        "state": state_param if state_param else "Punjab",
        "district": district_param if district_param else "Ludhiana",
        "tehsil": tehsil_param if tehsil_param else "Ludhiana West",
        "village": village_param if village_param else "Custom Locality",
        "registrationNumber": f"REG-2026-{(int(time.time()) % 9000) + 1000}",
        "registrationDate": "2026-01-15",
        "status": "Clear",
        "mortgage": "None",
        "courtCase": "None",
        "coordinates": resolved_coords,
        "latitude": lat,
        "longitude": lng,
        "geometry": dynamic_geom,
        "address": f"{village_param or 'Custom Locality'}, {tehsil_param or 'Ludhiana West'}, {district_param or 'Ludhiana'}, {state_param or 'Punjab'}"
    }
    
    # Register in properties_db so downstream analyze endpoint works
    properties_db[dynamic_prop["id"]] = dynamic_prop
    return jsonify(dynamic_prop)

@app.route('/api/document/analyze', methods=['POST'])
def analyze_document():
    # Simulate OCR Extraction Delay
    time.sleep(1.2)
    
    # Receive metadata to decide mock OCR data
    data = request.json or {}
    prop_id = data.get("propertyId", "PROP-001")
    
    # Generate mock OCR data customized for each property to simulate real verification discrepancies
    if prop_id == "PROP-001":
        # Rajesh Kumar's property: returns Ramesh Kumar (mismatch) and 2.8 acres (mismatch)
        ocr_result = {
            "ownerName": "Ramesh Kumar",
            "fatherName": "Ram Lal",
            "khasra": "123/4",
            "area": 2.8,
            "registrationNumber": "REG-2025-0192",
            "registrationDate": "2025-06-12",
            "address": "Malihabad Rural, Malihabad, Lucknow, Uttar Pradesh"
        }
    elif prop_id == "PROP-002":
        # Amit Sharma's property: returns Amit Sharma and 1.8 acres (exact match)
        ocr_result = {
            "ownerName": "Amit Sharma",
            "fatherName": "Som Nath",
            "khasra": "123/5",
            "area": 1.8,
            "registrationNumber": "REG-2025-0456",
            "registrationDate": "2025-08-20",
            "address": "Malihabad Rural, Malihabad, Lucknow, Uttar Pradesh"
        }
    elif prop_id == "PROP-003":
        # Sunita Devi's property: owner mismatch (Sunita Sen) to drop score below 60 (HIGH RISK)
        ocr_result = {
            "ownerName": "Sunita Sen",
            "fatherName": "Jagdish Prasad",
            "khasra": "123/6",
            "area": 3.2,
            "registrationNumber": "REG-2025-0789",
            "registrationDate": "2025-04-15",
            "address": "Malihabad Rural, Malihabad, Lucknow, Uttar Pradesh"
        }
    elif prop_id == "PROP-004":
        # Mohan Singh's property: exact matches
        ocr_result = {
            "ownerName": "Mohan Singh",
            "fatherName": "Gurnam Singh",
            "khasra": "124/1",
            "area": 1.2,
            "registrationNumber": "REG-2025-0222",
            "registrationDate": "2025-03-10",
            "address": "Malihabad Rural, Malihabad, Lucknow, Uttar Pradesh"
        }
    elif prop_id == "PROP-005":
        # Priya Gupta's property: Khasra mismatch and partial area mismatch (4.3 vs 4.1) for MEDIUM RISK
        ocr_result = {
            "ownerName": "Priya Gupta",
            "fatherName": "Ramesh Gupta",
            "khasra": "124/3",
            "area": 4.3,
            "registrationNumber": "REG-2025-0555",
            "registrationDate": "2025-07-05",
            "address": "Malihabad Rural, Malihabad, Lucknow, Uttar Pradesh"
        }
    else:
        # Fallback for custom simulated properties - dynamically matching searched location case-insensitively
        prop = None
        for pid, pdata in properties_db.items():
            if pid.lower() == prop_id.lower():
                prop = pdata
                break
                
        if prop:
            ocr_result = {
                "ownerName": "Ramesh Kumar" if prop["ownerName"] in ["Simulated Owner", "Custom Owner"] else prop["ownerName"],
                "fatherName": prop["fatherName"],
                "khasra": prop["khasra"],
                "area": prop["area"] + 0.6,
                "registrationNumber": prop["registrationNumber"],
                "registrationDate": prop["registrationDate"],
                "address": prop["address"]
            }
        else:
            ocr_result = {
                "ownerName": "Ramesh Kumar",
                "fatherName": "Ram Lal",
                "khasra": "123/4",
                "area": 2.8,
                "registrationNumber": "REG-2025-0192",
                "registrationDate": "2025-06-12",
                "address": "Village Gill, Ludhiana East, Ludhiana, Punjab"
            }
        
    return jsonify({
        "status": "success",
        "extractedData": ocr_result
    })

@app.route('/api/verify', methods=['POST'])
def verify_records():
    data = request.json or {}
    govt = data.get("govt")
    doc = data.get("doc")
    
    if not govt or not doc:
        return jsonify({"error": "Missing govt record or document data"}), 400
        
    # Implement dynamic scoring logic:
    # 1. Ownership (25 pts): Exact = 25, Partial = 20, Mismatch = 0
    owner_score = 0
    owner_status = "mismatch"
    govt_owner = str(govt.get("ownerName", "")).strip().lower()
    doc_owner = str(doc.get("ownerName", "")).strip().lower()
    
    if govt_owner == doc_owner:
        owner_score = 25
        owner_status = "match"
    else:
        # Partial match if surname or names overlap (excluding common stopwords)
        govt_words = set(govt_owner.split())
        doc_words = set(doc_owner.split())
        stopwords = {"kumar", "singh", "devi", "lal", "ram", "prasad", "sen", "sharma", "gupta"}
        intersection_clean = govt_words.intersection(doc_words) - stopwords
        if intersection_clean:
            owner_score = 20
            owner_status = "partial"
        else:
            owner_score = 0
            owner_status = "mismatch"
            
    # 2. Khasra (20 pts): Exact = 20, Mismatch = 0
    khasra_score = 0
    khasra_status = "mismatch"
    if str(govt.get("khasra", "")).strip() == str(doc.get("khasra", "")).strip():
        khasra_score = 20
        khasra_status = "match"
    else:
        khasra_score = 0
        khasra_status = "mismatch"
        
    # 3. Area (15 pts): Exact = 15, Partial (<=10% diff) = 7, Mismatch = 0
    area_score = 0
    area_status = "mismatch"
    try:
        govt_area = float(govt.get("area", 0))
        doc_area = float(doc.get("area", 0))
        if govt_area == doc_area:
            area_score = 15
            area_status = "match"
        else:
            diff_pct = abs(govt_area - doc_area) / govt_area
            if diff_pct <= 0.10:
                area_score = 7
                area_status = "partial"
            else:
                area_score = 0
                area_status = "mismatch"
    except Exception:
        area_score = 0
        area_status = "mismatch"
        
    # 4. Registration Match (15 pts): Exact = 15, Mismatch = 0
    reg_score = 0
    reg_status = "mismatch"
    if str(govt.get("registrationNumber", "")).strip() == str(doc.get("registrationNumber", "")).strip():
        reg_score = 15
        reg_status = "match"
    else:
        reg_score = 0
        reg_status = "mismatch"
        
    # 5. Encumbrance (10 pts): Clear = 10, Mortgage active = 0
    enc_score = 0
    enc_status = "active"
    mortgage = govt.get("mortgage", "None")
    if not mortgage or mortgage == "None" or mortgage == "":
        enc_score = 10
        enc_status = "clear"
    else:
        enc_score = 0
        enc_status = "active"
        
    # 6. Court Case Clear (10 pts): Clear = 10, Pending = 0
    court_score = 0
    court_status = "clear"
    court_case = govt.get("courtCase", "None")
    if not court_case or court_case == "None" or court_case == "":
        court_score = 10
        court_status = "clear"
    else:
        court_score = 0
        court_status = "pending"
        
    # 7. GIS Verification (5 pts)
    gis_score = 0
    gis_status = "mismatch"
    
    has_lat_lon = bool(govt.get("latitude") and govt.get("longitude"))
    has_geom = bool(govt.get("geometry") and govt.get("geometry", {}).get("type") == "Polygon")
    khasra_match_val = str(govt.get("khasra", "")).strip() == str(doc.get("khasra", "")).strip()
    
    govt_state = str(govt.get("state", "")).strip().lower()
    doc_address = str(doc.get("address", "")).strip().lower()
    loc_consistent = bool(govt_state and (govt_state in doc_address))
    
    area_consistent = False
    if has_geom:
        gis_area = calculate_parcel_area(govt.get("geometry"))
        try:
            g_area = float(govt.get("area", 0))
            if g_area > 0:
                diff_pct = abs(gis_area - g_area) / g_area
                if diff_pct <= 0.05:
                    area_consistent = True
        except Exception:
            pass
            
    if has_lat_lon:
        gis_score += 1
    if has_geom:
        gis_score += 1
    if khasra_match_val:
        gis_score += 1
    if loc_consistent:
        gis_score += 1
    if area_consistent:
        gis_score += 1
        
    if gis_score == 5:
        gis_status = "clear"
    elif gis_score >= 3:
        gis_status = "partial"
    else:
        gis_status = "mismatch"
        
    total_score = owner_score + khasra_score + area_score + reg_score + enc_score + court_score + gis_score
    
    # Calculate Risk Level
    if total_score >= 80:
        risk_level = "LOW"
    elif total_score >= 60:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"
        
    return jsonify({
        "score": total_score,
        "risk": risk_level,
        "breakdown": {
            "owner": {"score": owner_score, "max": 25, "status": owner_status},
            "khasra": {"score": khasra_score, "max": 20, "status": khasra_status},
            "area": {"score": area_score, "max": 15, "status": area_status},
            "registration": {"score": reg_score, "max": 15, "status": reg_status},
            "encumbrance": {"score": enc_score, "max": 10, "status": enc_status},
            "court": {"score": court_score, "max": 10, "status": court_status},
            "gis": {"score": gis_score, "max": 5, "status": gis_status}
        }
    })

@app.route('/api/verification-history', methods=['GET', 'POST'])
def handle_history():
    global verification_history
    if request.method == 'POST':
        new_entry = request.json
        if new_entry:
            new_entry["id"] = len(verification_history) + 1
            new_entry["date"] = time.strftime("%d %b %Y")
            verification_history.append(new_entry)
            return jsonify(new_entry), 201
        return jsonify({"error": "Invalid data"}), 400
    else:
        return jsonify(verification_history)

if __name__ == '__main__':
    app.run(port=5005, debug=True)
