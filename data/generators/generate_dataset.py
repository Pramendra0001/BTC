import argparse
import random
import json
import csv
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import hashlib
import os

SCENARIO_WEIGHTS = {
    "NORMAL_BASELINE": 0.60,
    "BURST_ACTIVITY": 0.08,
    "FAN_OUT_PEELING": 0.06,
    "FAN_IN_CONSOLIDATION": 0.06,
    "AMOUNT_ANOMALY": 0.05,
    "GEO_HOPPING": 0.05,
    "MULTI_SIGNAL_ANOMALY": 0.10
}

SCRIPT_TYPES = ["p2pkh", "p2sh", "p2wpkh", "p2wsh", "p2tr"]
COUNTRIES = ["US", "RU", "CN", "DE", "NL", "RO", "UA", "GB", "JP", "KR", "IR", "VE", "NG"]
ASNS = ["AS13335", "AS15169", "AS16509", "AS714", "AS174", "AS2914", "AS3356", "AS3215"]

def generate_txid():
    return hashlib.sha256(str(random.random()).encode()).hexdigest()

def generate_address(script_type):
    if script_type == "p2pkh":
        return "1" + "".join(random.choices("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz", k=33))
    elif script_type == "p2sh":
        return "3" + "".join(random.choices("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz", k=33))
    elif script_type.startswith("p2w"):
        return "bc1" + "".join(random.choices("qpzry9x8gf2tvdw0s3jn54khce6mua7l", k=39))
    else:
        return "bc1p" + "".join(random.choices("qpzry9x8gf2tvdw0s3jn54khce6mua7l", k=58))

def generate_ip():
    return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"

def generate_record(timestamp, scenario):
    script_type = random.choice(SCRIPT_TYPES)
    
    src_ip = generate_ip()
    dst_ip = generate_ip()
    src_port = random.randint(1024, 65535)
    dst_port = 8333
    txid = generate_txid()
    geo_country = random.choice(COUNTRIES)
    asn = random.choice(ASNS)
    
    num_inputs = 1
    num_outputs = 2
    total_val = random.randint(10000, 100000000)
    fee = random.randint(1000, 50000)
    
    if scenario == "FAN_OUT_PEELING":
        num_outputs = random.randint(5, 50)
    elif scenario == "FAN_IN_CONSOLIDATION":
        num_inputs = random.randint(5, 50)
        num_outputs = 1
    elif scenario == "AMOUNT_ANOMALY":
        total_val = random.randint(10000000000, 100000000000)
        fee = random.randint(1000000, 5000000)
    
    input_amounts = []
    output_amounts = []
    
    remaining = total_val
    for i in range(num_outputs - 1):
        amt = remaining // (num_outputs - i)
        output_amounts.append(amt)
        remaining -= amt
    output_amounts.append(remaining - fee)
    
    remaining_in = total_val
    for i in range(num_inputs - 1):
        amt = remaining_in // (num_inputs - i)
        input_amounts.append(amt)
        remaining_in -= amt
    input_amounts.append(remaining_in)

    input_addresses = [generate_address(script_type) for _ in range(num_inputs)]
    output_addresses = [generate_address(script_type) for _ in range(num_outputs)]
    
    return {
        "timestamp": timestamp.isoformat() + "Z",
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "src_port": src_port,
        "dst_port": dst_port,
        "txid": txid,
        "input_addresses": ";".join(input_addresses),
        "output_addresses": ";".join(output_addresses),
        "input_amounts": ";".join(map(str, input_amounts)),
        "output_amounts": ";".join(map(str, output_amounts)),
        "fee": fee,
        "script_type": script_type,
        "geo_country": geo_country,
        "asn": asn,
        "scenario_label": scenario
    }

def main():
    parser = argparse.ArgumentParser(description="BTC-SHIELD Synthetic Data Generator")
    parser.add_argument("--size", type=int, default=1000, help="Number of records to generate")
    parser.add_argument("--format", type=str, choices=["csv", "json", "xml"], default="csv", help="Output format")
    parser.add_argument("--output", type=str, default="../samples/", help="Output directory")
    args = parser.parse_args()
    
    random.seed(42)
    os.makedirs(args.output, exist_ok=True)
    
    scenarios, weights = zip(*SCENARIO_WEIGHTS.items())
    start_time = datetime.utcnow() - timedelta(days=30)
    
    records = []
    for i in range(args.size):
        scenario = random.choices(scenarios, weights=weights, k=1)[0]
        # Burst activity clustering
        if scenario == "BURST_ACTIVITY" and i > 0 and records[-1]["scenario_label"] == "BURST_ACTIVITY":
            timestamp = datetime.fromisoformat(records[-1]["timestamp"].replace("Z", "")) + timedelta(seconds=random.randint(1, 5))
        else:
            timestamp = start_time + timedelta(seconds=random.randint(0, 30*24*3600))
        
        record = generate_record(timestamp, scenario)
        
        if scenario == "GEO_HOPPING" and i > 0:
            record["input_addresses"] = records[-1]["input_addresses"]
            record["geo_country"] = random.choice([c for c in COUNTRIES if c != records[-1]["geo_country"]])
        
        records.append(record)
        
    records.sort(key=lambda x: x["timestamp"])
    
    filename = os.path.join(args.output, f"dataset_{args.size}.{args.format}")
    
    if args.format == "csv":
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=records[0].keys())
            writer.writeheader()
            writer.writerows(records)
    elif args.format == "json":
        with open(filename, 'w') as f:
            json.dump(records, f, indent=2)
    elif args.format == "xml":
        root = ET.Element("Transactions")
        for rec in records:
            tx = ET.SubElement(root, "Transaction")
            for k, v in rec.items():
                child = ET.SubElement(tx, k)
                child.text = str(v)
        tree = ET.ElementTree(root)
        tree.write(filename, encoding='utf-8', xml_declaration=True)
        
    print(f"Generated {args.size} records in {filename}")

if __name__ == "__main__":
    main()
