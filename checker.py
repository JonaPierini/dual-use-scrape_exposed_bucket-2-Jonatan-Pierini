import json
import requests


def check_buckets():
  try:
    with open("results.json", "r") as f:
      data = json.load(f)
      buckets = data.get("scraper", {}).get("discovered_buckets", [])
  except FileNotFoundError:
    print("results.json no encontrado. Ejecuta primero scraper.py")
    return

  checked_buckets = []

  for b in buckets:
    bucket_name = b["bucket_name"]
    endpoint = b["endpoint"]

    list_status = "failed"
    read_status = "failed"

    # Intento de list objects anónimo
    try:
      list_url = f"{endpoint}/{bucket_name}?list-type=2"
      res = requests.get(list_url, timeout=3)
      if res.status_code in [200, 403]:
        list_status = "success"
    except Exception:
      pass

    # Intento de read object anónimo (archivo de prueba común)
    try:
      read_url = f"{endpoint}/{bucket_name}/test.txt"
      res = requests.get(read_url, timeout=3)
      if res.status_code == 200:
        read_status = "success"
    except Exception:
      pass

    checked_buckets.append({
        "bucket_name": bucket_name,
        "endpoint": endpoint,
        "list_objects": list_status,
        "read_object": read_status,
    })

  # Generar summary.json con la estructura exacta solicitada
  summary_data = {"buckets": checked_buckets}
  with open("summary.json", "w") as f:
    json.dump(summary_data, f, indent=4)
  print("summary.json generado exitosamente.")

  # Actualizar la sección checker dentro de results.json
  try:
    with open("results.json", "r") as f:
      results = json.load(f)
    results["checker"] = {"buckets": checked_buckets}
    with open("results.json", "w") as f:
      json.dump(results, f, indent=4)
    print("results.json actualizado con los resultados del checker.")
  except Exception as e:
    print(f"Error actualizando results.json: {e}")


if __name__ == "__main__":
  print("Iniciando checker...")
  check_buckets()