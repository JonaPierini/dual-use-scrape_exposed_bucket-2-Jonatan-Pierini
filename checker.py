import requests
import json
import xml.etree.ElementTree as ET

def check_buckets():
    try:
        with open("results.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Ejecuta scraper.py primero.")
        return

    summary_buckets = []

    for b in data["scraper"]["discovered_buckets"]:
        bucket = b["bucket_name"]
        endpoint = b["endpoint"]
        list_status = "failed"
        read_status = "failed"

        # 1. Intentar List Objects anónimo
        list_url = f"{endpoint}/{bucket}"
        try:
            res = requests.get(list_url, timeout=5)
            if res.status_code == 200:
                list_status = "success"
                
                # 2. Intentar Read Object de algún archivo encontrado en el XML
                try:
                    root = ET.fromstring(res.text)
                    keys = root.findall('.//{http://s3.amazonaws.com/doc/2006-03-01/}Key')
                    if not keys:
                        keys = root.findall('.//Key')

                    if keys:
                        first_file = keys[0].text
                        read_url = f"{endpoint}/{bucket}/{first_file}"
                        read_res = requests.get(read_url, timeout=5)
                        if read_res.status_code == 200:
                            read_status = "success"
                except Exception as xml_e:
                    print(f"Error parseando XML del bucket {bucket}: {xml_e}")

        except Exception as e:
            print(f"Error conectando al bucket {bucket}: {e}")

        summary_buckets.append({
            "bucket_name": bucket,
            "endpoint": endpoint,
            "list_objects": list_status,
            "read_object": read_status
        })

    data["checker"]["buckets"] = summary_buckets
    with open("results.json", "w") as f:
        json.dump(data, f, indent=4)

    summary = {"buckets": summary_buckets}
    with open("summary.json", "w") as f:
        json.dump(summary, f, indent=4)

    print("Checker finalizado. summary.json creado.")

if __name__ == "__main__":
    check_buckets()