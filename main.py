import requests
import pandas as pd
import matplotlib.pyplot as plt
import os

# --- Configuration ---
# IMPORTANT: You need to obtain an API key from NHTSA for their Crash API.
# Visit the NHTSA website or API documentation to register and get your key.
NHTSA_API_KEY = "YOUR_NHTSA_API_KEY"  # <--- REPLACE THIS WITH YOUR ACTUAL API KEY!

# A simple map for state full names to 2-letter codes.
# You might need to expand this or ensure the API uses specific codes.
STATE_CODE_MAP = {
    "ALABAMA": "AL", "ALASKA": "AK", "ARIZONA": "AZ", "ARKANSAS": "AR",
    "CALIFORNIA": "CA", "COLORADO": "CO", "CONNECTICUT": "CT", "DELAWARE": "DE",
    "FLORIDA": "FL", "GEORGIA": "GA", "HAWAII": "HI", "IDAHO": "ID",
    "ILLINOIS": "IL", "INDIANA": "IN", "IOWA": "IA", "KANSAS": "KS",
    "KENTUCKY": "KY", "LOUISIANA": "LA", "MAINE": "ME", "MARYLAND": "MD",
    "MASSACHUSETTS": "MA", "MICHIGAN": "MI", "MINNESOTA": "MN", "MISSISSIPPI": "MS",
    "MISSOURI": "MO", "MONTANA": "MT", "NEBRASKA": "NE", "NEVADA": "NV",
    "NEW HAMPSHIRE": "NH", "NEW JERSEY": "NJ", "NEW MEXICO": "NM", "NEW YORK": "NY",
    "NORTH CAROLINA": "NC", "NORTH DAKOTA": "ND", "OHIO": "OH", "OKLAHOMA": "OK",
    "OREGON": "OR", "PENNSYLVANIA": "PA", "RHODE ISLAND": "RI", "SOUTH CAROLINA": "SC",
    "SOUTH DAKOTA": "SD", "TENNESSEE": "TN", "TEXAS": "TX", "UTAH": "UT",
    "VERMONT": "VT", "VIRGINIA": "VA", "WASHINGTON": "WA", "WEST VIRGINIA": "WV",
    "WISCONSIN": "WI", "WYOMING": "WY",
    "DISTRICT OF COLUMBIA": "DC"
}


# ---------------------------
# Step 1: Fetch Data from NHTSA Crash API
# ---------------------------
def fetch_crash_data(year=2023, state=None):
    """
    Fetches crash data from the NHTSA Crash API for a given year and optional state.
    Note: The NHTSA API typically requires an API key and often specific parameters
    like state or location for meaningful data retrieval. A general 'crashes'
    endpoint for all national data is usually not available without specific filters.
    We are using a hypothetical 'GetCrashesByLocation' style endpoint as an example.
    """
    if NHTSA_API_KEY == "YOUR_NHTSA_API_KEY":
        print("❌ Error: Please replace 'YOUR_NHTSA_API_KEY' with your actual NHTSA API key.")
        return []

    # This is a placeholder URL. You must verify the correct endpoint from NHTSA API documentation.
    # Common endpoints require state code and year for retrieving crash summaries/details.
    # Example: A common pattern might be 'GetCrashesByLocation' or similar.
    # For bulk data, you might need to iterate through months or use specific data downloads.
    base_url = "https://crashviewer.nhtsa.dot.gov/CrashAPI/crashes/GetCrashesByLocation"  # Example endpoint

    params = {
        "format": "json",
        "year": year,
        "API_KEY": NHTSA_API_KEY
    }

    state_code = None
    if state:
        state_upper = state.upper()
        state_code = STATE_CODE_MAP.get(state_upper, state_upper)  # Try map, then use as-is
        params["state"] = state_code  # Add state parameter

    try:
        location_info = f" for {year}" + (f" ({state_code})" if state_code else "")
        print(f"📡 Fetching crash data{location_info}...")

        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        # The actual data might be nested. Check NHTSA API documentation for the structure.
        # It's common for results to be in 'Results' key, often with further nesting.
        results = data.get("Results", [])
        if results and isinstance(results, list) and len(results) > 0:
            # Assuming the actual crash data is the first item in the Results list
            # and it's a list of crash records. This is a common API response pattern.
            crash_records = results[0]
            print(f"✅ Data fetched successfully. Found {len(crash_records)} crash records.")
            return crash_records
        else:
            print("⚠️ No 'Results' or empty 'Results' found in API response.")
            print(f"API Response (sample): {str(data)[:500]}...")  # Print a snippet for debugging
            return []

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch crash data due to network or API error: {e}")
        return []
    except ValueError as e:
        print(f"❌ Failed to parse JSON response: {e}")
        return []
    except Exception as e:
        print(f"❌ An unexpected error occurred during data fetching: {e}")
        return []


# ---------------------------
# Step 2: Extract Vehicle Make Info
# ---------------------------
def extract_vehicle_makes(crash_data):
    """
    Extracts vehicle makes from a list of crash data dictionaries.
    IMPORTANT: The exact key for 'vehicleMake' depends on the NHTSA API response structure.
    You might need to adjust 'crash["vehicleMake"]' if it's nested (e.g., crash['Vehicles'][0]['MakeName']).
    """
    makes = []
    if not crash_data:
        print("⚠️ No crash data provided for extraction.")
        return pd.Series(makes)

    for i, crash in enumerate(crash_data):
        # This is the most common place to need adjustment based on actual API data.
        # Inspect the actual JSON response from NHTSA to confirm the path to vehicle make.
        # Example if it's nested: crash.get('Vehicles', [{}])[0].get('MakeName')
        vehicle_make = crash.get("vehicleMake")  # Assumes 'vehicleMake' is a direct key
        if vehicle_make:
            makes.append(str(vehicle_make).strip())  # Ensure it's a string and trim whitespace
        else:
            # Optional: print a warning if a crash record doesn't have a vehicle make
            # print(f"Warning: Crash record {i} missing 'vehicleMake' key or value.")
            pass

    if not makes:
        print("⚠️ No vehicle makes could be extracted from the provided data. Check 'vehicleMake' key.")
    return pd.Series(makes)


# ---------------------------
# Step 3: Analyze Top Brands
# ---------------------------
def get_top_vehicle_brands(make_series, top_n=10):
    """
    Calculates the frequency of vehicle makes and returns the top N brands.
    """
    if make_series.empty:
        print("⚠️ Vehicle make series is empty. Cannot determine top brands.")
        return pd.Series()
    return make_series.value_counts().head(top_n)


# ---------------------------
# Step 4: Plot
# ---------------------------
def plot_top_brands(brand_counts):
    """
    Generates a bar plot of the top vehicle brands.
    """
    if brand_counts.empty:
        print("⚠️ No data to plot for top brands.")
        return

    plt.figure(figsize=(12, 7))  # Increased figure size for better readability
    brand_counts.plot(kind="bar", color="navy", edgecolor="black")
    plt.title("Top Vehicle Brands in Crashes", fontsize=16)
    plt.xlabel("Vehicle Brand", fontsize=12)
    plt.ylabel("Crash Count", fontsize=12)
    plt.xticks(rotation=45, ha='right', fontsize=10)  # Rotate and align for better labels
    plt.yticks(fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.7)  # Add a grid for readability
    plt.tight_layout()  # Adjust layout to prevent labels from being cut off
    plt.show()


# ---------------------------
# Step 5: Orchestrate It All
# ---------------------------
def main():
    year = 2023
    # Try a specific state like 'MI' or 'California'.
    # Leaving it None might result in no data if the API requires a state.
    state = "MI"  # Example: Set to 'MI' for Michigan, or 'California' for California

    # Create outputs directory if it doesn't exist
    output_dir = "outputs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: '{output_dir}'")

    crash_data = fetch_crash_data(year=year, state=state)
    if not crash_data:
        print("🚫 No crash data retrieved. Please check API key, endpoint, and parameters.")
        return

    make_series = extract_vehicle_makes(crash_data)
    if make_series.empty:
        print("🚫 No vehicle makes extracted. Cannot proceed with analysis.")
        return

    top_brands = get_top_vehicle_brands(make_series)

    if not top_brands.empty:
        print("\n📊 Top Vehicle Brands:")
        print(top_brands)

        csv_path = os.path.join(output_dir, "top_vehicle_brands.csv")
        top_brands.to_csv(csv_path, index_label="Vehicle Brand")  # Add index_label for CSV header
        print(f"\n✅ Saved top brands to '{csv_path}'")

        plot_top_brands(top_brands)
    else:
        print("\n⚠️ No top brands to display or save.")


if __name__ == "__main__":
    main()