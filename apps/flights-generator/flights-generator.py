import time
from minio import Minio
import random as rn
import io
import csv
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

Airports = ["LAX", "JFK", "ABQ", "AAR", "SMP", "RMP", "LAH", "RAM"]
UniqueCarrier = ["AA", "DL", "NK", "HA"]


# Initialize Minio client
minio_client = Minio(
    endpoint=os.getenv("ENDPOINT"),  
    access_key=os.getenv("ACCESS_KEY"),
    secret_key=os.getenv("SECRET_KEY"),
    secure=False,  # Change to True if using HTTPS
)


# Function to generate fake flight data
def generate_flight_data():
    return {
        "Year": rn.randint(2010, 2024),
        "Month": rn.randint(1, 12),
        "DayofMonth": rn.randint(1, 31),
        "DayOfWeek": rn.randint(1, 7),
        "Origin": rn.choice(Airports),
        "Dest": rn.choice(Airports),
        "DepTime": f"{rn.randint(0,23)}{rn.randint(0,59)}",
        "ArrTime": f"{rn.randint(0,23)}{rn.randint(0,59)}",
        "UniqueCarrier": rn.choice(UniqueCarrier),
        "DepDelay": rn.randint(-30, 200),
    }


# Function to upload data to Minio
def upload_to_minio(bucket_name, file_name, data):
    try:
        data_bytes = data.encode("utf-8")
        data_stream = io.BytesIO(data_bytes)
        minio_client.put_object(bucket_name, file_name, data_stream, len(data_bytes))
        print(f"Uploaded {file_name} to Minio bucket {bucket_name}")
    except Exception as err:
        print(err)


# Main function to generate and upload fake flight data
def main():
    bucket_name = os.getenv("BUCKET")

    while True:
        # Generate fake flight data
        flight_data = generate_flight_data()

        # Define filename
        file_name = f"flights_{rn.randint(1, 9999)}.csv"

        # Convert dictionary to CSV string
        csv_data = io.StringIO()
        columns = list(flight_data.keys())
        csv_writer = csv.DictWriter(csv_data, fieldnames=columns)
        csv_writer.writeheader()
        
        for i in range(1, 100):
            flight_data = generate_flight_data()
            csv_writer.writerow(flight_data)
        
        csv_content = csv_data.getvalue()

        # Upload to Minio
        upload_to_minio(bucket_name, file_name, csv_content)

        # Wait 
        time.sleep(60)


if __name__ == "__main__":
    main()
