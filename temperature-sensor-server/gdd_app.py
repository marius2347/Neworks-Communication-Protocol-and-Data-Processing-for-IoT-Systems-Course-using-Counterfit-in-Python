import csv
from datetime import datetime, date
import json

def calculate_gdd(base_temp, csv_file='temperature.csv'):
    """
    Calculate Growing Degree Days (GDD) from temperature data.

    Args:
        base_temp (float): Base temperature for the plant in Celsius
        csv_file (str): Path to the CSV file containing temperature data

    Returns:
        dict: Dictionary with dates as keys and GDD values as values
    """
    daily_temps = {}

    # Read temperature data
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                # Parse date
                dt = datetime.fromisoformat(row['date'])
                day = dt.date()

                # Parse temperature - assuming format "[val1, val2]" where val2 is temperature
                temp_str = row['temperature'].strip('[]')
                temp_values = [float(x.strip()) for x in temp_str.split(',')]
                temperature = temp_values[1]  # Assuming second value is the temperature

                # Collect temperatures for each day
                if day not in daily_temps:
                    daily_temps[day] = []
                daily_temps[day].append(temperature)

            except (ValueError, IndexError) as e:
                print(f"Error parsing row: {row} - {e}")
                continue

    # Calculate GDD for each day
    gdd_results = {}
    for day, temps in daily_temps.items():
        if temps:
            high = max(temps)
            low = min(temps)
            avg_temp = (high + low) / 2
            gdd = max(0, avg_temp - base_temp)  # GDD can't be negative
            gdd_results[day] = {
                'high': high,
                'low': low,
                'avg': avg_temp,
                'gdd': gdd
            }

    return gdd_results

def main():
    # Example usage for strawberries (base temp 10°C)
    base_temp = 10.0
    plant_name = "Strawberries"

    print(f"Calculating GDD for {plant_name} (base temperature: {base_temp}°C)")
    print("-" * 60)

    gdd_data = calculate_gdd(base_temp)

    if not gdd_data:
        print("No temperature data found.")
        return

    total_gdd = 0
    for day in sorted(gdd_data.keys()):
        data = gdd_data[day]
        total_gdd += data['gdd']
        print(f"{day}: High={data['high']:.1f}°C, Low={data['low']:.1f}°C, "
              f"Avg={data['avg']:.1f}°C, GDD={data['gdd']:.1f}")

    print("-" * 60)
    print(f"Total GDD accumulated: {total_gdd:.1f}")
    print(f"Strawberries typically need ~250 GDD to bear fruit.")

if __name__ == "__main__":
    main()
