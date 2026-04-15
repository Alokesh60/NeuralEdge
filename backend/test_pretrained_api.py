import requests
import json

url = "http://localhost:8000/audit/tabular/flexible"

# Open files
with open("adult_with_header.csv", "rb") as f_csv, \
     open("my_pretrained_model.pkl", "rb") as f_model, \
     open("my_pretrained_preprocessor.pkl", "rb") as f_pre:

    files = {
        "file": ("adult_with_header.csv", f_csv, "text/csv"),
        "model_file": ("my_pretrained_model.pkl", f_model, "application/octet-stream"),
        "preprocessor_file": ("my_pretrained_preprocessor.pkl", f_pre, "application/octet-stream"),
    }
    data = {
        "target_column": "income",
        "sensitive_columns": "sex",
        "privileged_values": '{"sex":"Male"}',   # valid JSON string
        "model_choice": "ignored",
    }

    response = requests.post(url, files=files, data=data)
    print("Status:", response.status_code)
    if response.status_code == 200:
        result = response.json()
        print("Model name:", result.get("model_name"))
        print("Verdict:", result["overall"]["verdict"])
        print("Disparate Impact:", result["overall"]["disparate_impact"])
        print("Pretrained mode active? (model_name == 'pretrained')", result.get("model_name") == "pretrained")
    else:
        print("Error:", response.text)