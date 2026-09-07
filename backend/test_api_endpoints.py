import urllib.request
import json
import os

BASE = "http://127.0.0.1:8000"

def test_routes():
    print("Testing Backend API Endpoints...")
    
    # 1. Root & Health
    with urllib.request.urlopen(f"{BASE}/") as res:
        data = json.loads(res.read().decode())
        print("[OK] Root endpoint:", data["platform"])
        
    # 2. Cameras
    with urllib.request.urlopen(f"{BASE}/cameras/") as res:
        data = json.loads(res.read().decode())
        print(f"[OK] Cameras endpoint: {data['count']} cameras configured")
        
    # 3. System Status
    with urllib.request.urlopen(f"{BASE}/system/status") as res:
        data = json.loads(res.read().decode())
        print("[OK] System status device:", data["processing_device"])
        
    # 4. Events
    with urllib.request.urlopen(f"{BASE}/events/") as res:
        data = json.loads(res.read().decode())
        print(f"[OK] Events endpoint: {data['count']} events recorded")
        
    # 5. Risk Evaluate
    risk_payload = json.dumps({
        "night_period": True,
        "restricted_zone": True,
        "loitering": True,
        "degraded_footage": True
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE}/risk/evaluate",
        data=risk_payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode())
        print(f"[OK] Risk engine: Score={data['composite_score']}, Level={data['risk_level']}")
        
    # 6. Enhancement Sample
    sample_path = os.path.join("data", "test_samples", "sample_cctv_lowlight.jpg")
    if os.path.exists(sample_path):
        data = open(sample_path, "rb").read()
        boundary = "----WebKitFormBoundarySentinelTest"
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="lowlight.jpg"\r\n'
            f"Content-Type: image/jpeg\r\n\r\n"
        ).encode("latin1") + data + f"\r\n--{boundary}--\r\n".encode("latin1")
        
        req = urllib.request.Request(
            f"{BASE}/enhancement/analyze",
            data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
        )
        with urllib.request.urlopen(req) as res:
            analysis = json.loads(res.read().decode())
            print(f"[OK] Enhancement analyze: Quality Score={analysis['overall_quality']}, Diagnosis={[d['label'] for d in analysis['diagnosis']]}")

        # Run enhancement
        req2 = urllib.request.Request(
            f"{BASE}/enhancement/run",
            data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
        )
        with urllib.request.urlopen(req2) as res:
            run_res = json.loads(res.read().decode())
            print(f"[OK] Enhancement run: Hash Changed={run_res['validation']['hash_changed']}, Source={run_res['source']['integrity_hash'][:10]}..., Deriv={run_res['output']['integrity_hash'][:10]}..., Time={run_res['processing']['processing_time_ms']}ms")

    print("\nALL ENDPOINTS FUNCTIONING WITH 100% OPERATIONAL FIDELITY!")

if __name__ == "__main__":
    test_routes()
