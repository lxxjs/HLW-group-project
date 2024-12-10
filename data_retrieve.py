import os
import re
import time
import json
from datetime import datetime, timedelta
import requests

OUTPUT_DIR = "bgp_updates"
os.makedirs(OUTPUT_DIR, exist_ok=True)

PREFIX_DIR = "as_prefixes"

end_time = datetime.utcnow()
start_time = end_time - timedelta(days=7)
end_time_str = end_time.strftime("%Y-%m-%dT%H:%M")
start_time_str = start_time.strftime("%Y-%m-%dT%H:%M")

prefix_files = [f for f in os.listdir(PREFIX_DIR) if f.endswith('.txt')]

asn_pattern = re.compile(r'AS(\d+)')

for prefix_file in prefix_files:
    match = asn_pattern.search(prefix_file)
    if match:
        asn = match.group(1)
    else:
        print(f"Cannot extract ASN from filename {prefix_file}. Skipping...")
        continue

    print(f"Processing AS{asn} prefixes...")
    
    file_path = os.path.join(PREFIX_DIR, prefix_file)
    with open(file_path, 'r') as f:
        prefixes = [line.strip() for line in f if line.strip()]
    
    for prefix in prefixes:
        print("-------------------------------------------")
        print(f"Fetching BGP updates for prefix {prefix}...")
        
        # BGP Update API request
        api_url = f"https://stat.ripe.net/data/bgp-updates/data.json?resource={prefix}&starttime={start_time_str}&endtime={end_time_str}"
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()
            nr_updates = data.get('data', {}).get('nr_updates', 0)
            if nr_updates == 0:
                print("No updates. Skipping...")
                continue
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {prefix}: {e}")
            continue

        # Safe prefix format: "100.0/16" -> "100.0_16"
        safe_prefix = prefix.replace('/', '_')
        
        # Save response
        output_file = os.path.join(OUTPUT_DIR, f"bgp_updates_{safe_prefix}.json")
        with open(output_file, 'w') as out_f:
            json.dump(data, out_f, indent=4)
        
        print(f"BGP 업데이트 데이터가 {output_file}에 저장되었습니다.")
        print("-------------------------------------------")
        
        time.sleep(1)

print("-------------------------------------------")
print("All BGP update data collection completed.")
