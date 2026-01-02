import csv
import collections
import json

def analyze_deveui_prefixes(filename):
    prefix_map = collections.defaultdict(lambda: {'manufacturers': set(), 'models': set()})
    
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            deveui = row['DevEUI'].upper().strip().replace('"', '')
            manufacturer = row['Manufacturer'].strip()
            model = row['Model'].strip()
            
            if not deveui or len(deveui) < 8:
                continue

            for length in [6, 7, 8, 9, 10, 11, 12]:
                prefix = deveui[:length]
                prefix_map[prefix]['manufacturers'].add(manufacturer)
                prefix_map[prefix]['models'].add(model)

    # Filter for uniqueness
    results = {
        "manufacturers_by_prefix": {},
        "models_by_prefix": {}
    }
    
    # Manufacturers
    # We want strict mapping: if prefix X maps to only 1 Manufacturer, it's a rule.
    for prefix, data in prefix_map.items():
        if len(data['manufacturers']) == 1:
            results["manufacturers_by_prefix"][prefix] = list(data['manufacturers'])[0]

    # Models
    for prefix, data in prefix_map.items():
         if len(data['models']) == 1:
             results["models_by_prefix"][prefix] = list(data['models'])[0]

    with open('deveui_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

analyze_deveui_prefixes('Equipement - Feuille 1.csv')
