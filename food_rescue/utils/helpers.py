import json
from datetime import datetime

# Load JSON data
def load_json(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

# Save JSON data
def save_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

# Calculate metrics
def calculate_total_food_rescued(delivery_log):
    return sum([entry["quantity_kg"] for entry in delivery_log if entry["status"]=="Delivered"])

def calculate_meals_saved(total_food):
    return total_food / 0.5

def calculate_co2_reduced(total_food):
    return total_food * 2.5

def calculate_avg_pickup_time(delivery_log):
    times = []
    for entry in delivery_log:
        if entry["status"]=="Delivered":
            accepted = datetime.strptime(entry["accepted_time"], "%H:%M")
            picked_up = datetime.strptime(entry["pickup_time"], "%H:%M")
            times.append((picked_up - accepted).seconds / 60)  # in minutes
    return sum(times)/len(times) if times else 0
