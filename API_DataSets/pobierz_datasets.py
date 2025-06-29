import requests
import pandas as pd
import openpyxl  # wymagany silnik dla .xlsx
import time

# Konfiguracja API
BASE_URL = "https://api.dane.gov.pl/1.4/datasets"
PER_PAGE = 20
SLEEP_TIME = 0.5

# Pobierz liczbę wszystkich rekordów
initial_res = requests.get(f"{BASE_URL}?page=1&per_page=1")
initial_res.raise_for_status()
total_count = int(initial_res.json().get("meta", {}).get("count", 0))
total_pages = (total_count // PER_PAGE) + 1

print(f"📦 Łączna liczba rekordów: {total_count} (stron: {total_pages})")

rows = []

# Iteracja po wszystkich stronach API
for page in range(1, total_pages + 1):
    print(f"➡️ Pobieranie strony {page}/{total_pages}")
    try:
        res = requests.get(f"{BASE_URL}?page={page}&per_page={PER_PAGE}")
        res.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Błąd pobierania strony {page}: {e}")
        break

    data = res.json().get("data", [])

    for dataset in data:
        attr = dataset.get("attributes", {})
        rel = dataset.get("relationships", {})

        rows.append({
            "ID": dataset.get("id", ""),
            "Tytuł": attr.get("title", ""),
            "Opis": attr.get("notes", ""),
            "Licencja": attr.get("license_name", ""),
            "Data utworzenia": attr.get("created", ""),
            "Data modyfikacji": attr.get("modified", ""),
            "Kategorie": ", ".join([c.get("title", "") for c in attr.get("categories", [])]),
            "Częstotliwość aktualizacji": attr.get("update_frequency", ""),
            "Formaty": ", ".join(attr.get("formats", [])),
            "Instytucja (link)": rel.get("institution", {}).get("links", {}).get("related", ""),
            "Zasoby (link)": rel.get("resources", {}).get("links", {}).get("related", ""),
            "Liczba zasobów": rel.get("resources", {}).get("meta", {}).get("count", 0)
        })

    time.sleep(SLEEP_TIME)

# Konwersja do DataFrame i zapis do Excel
df = pd.DataFrame(rows)
df.to_excel("zasoby_dane_gov.xlsx", index=False, engine="openpyxl")
print("✅ Zapisano plik: zasoby_dane_gov.xlsx")
