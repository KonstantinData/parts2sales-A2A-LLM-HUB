import datetime, os
def run_daily():
    today = datetime.date.today().isoformat()
    input_file = f"data/inputs/{today}_articles_raw.jsonl"
    output_dir = f"outputs/{today}/"
    os.makedirs(output_dir, exist_ok=True)
    # Hier: Lade Daten, durchlaufe Pipeline, speichere Outputs
if __name__ == "__main__":
    run_daily()
