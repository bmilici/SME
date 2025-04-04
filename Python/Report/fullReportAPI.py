import requests
import base64
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import time
import os

# Define your Five9 API credentials
username = ""  # Update with your Username
password = ""  # Update with your Password

# Encode the credentials
credentials = base64.b64encode(f"{username}:{password}".encode()).decode()

# Define the URL of the SOAP API
url = "https://api.five9.com:443/wsadmin/v12/AdminWebService"

# Define headers with Content-Type and Authorization
headers = {
    "Content-Type": "text/xml;charset=UTF-8",
    "Authorization": f"Basic {credentials}"
}

def run_report(folder_name, report_name, start_timestamp, end_timestamp):
    # Define the SOAP envelope with the runReport request
    soap_envelope = f"""
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ser="http://service.admin.ws.five9.com/">
        <soapenv:Header/>
        <soapenv:Body>
            <ser:runReport>
                <folderName>{folder_name}</folderName>
                <reportName>{report_name}</reportName>
                <criteria>
                    <time>
                        <start>{start_timestamp}</start>
                        <end>{end_timestamp}</end>
                    </time>
                </criteria>
            </ser:runReport>
        </soapenv:Body>
    </soapenv:Envelope>
    """

    # Send POST request with SOAP envelope as data
    response = requests.post(url, data=soap_envelope, headers=headers)

    # Extract report_identifier from the response
    try:
        root = ET.fromstring(response.content)
        report_identifier = root.find('.//return').text
        print("Report Identifier for", folder_name, ":", report_identifier)
        return report_identifier
    except Exception as e:
        print("Failed to extract report identifier from response:", e)
        print("Response content:", response.content)
        return None

def is_report_running(report_identifier):
    # Define the SOAP envelope to check if the report is running
    is_report_running_soap = f"""
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ser="http://service.admin.ws.five9.com/">
       <soapenv:Header/>
       <soapenv:Body>
          <ser:isReportRunning>
             <identifier>{report_identifier}</identifier>
          </ser:isReportRunning>
       </soapenv:Body>
    </soapenv:Envelope>
    """

    # Send POST request to check if the report is running
    response = requests.post(url, data=is_report_running_soap, headers=headers)

    # Parse the response and return True if the report is running, False otherwise
    try:
        root = ET.fromstring(response.content)
        is_running = root.find('.//return').text
        print("Report is running:", is_running)
        return is_running.lower() == "true"
    except Exception as e:
        print("Failed to parse isReportRunning response:", e)
        return False

def get_report_results_csv(report_identifier):
    # Define the SOAP envelope to get the report results
    get_report_result_soap = f"""
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ser="http://service.admin.ws.five9.com/">
       <soapenv:Header/>
       <soapenv:Body>
          <ser:getReportResultCsv>
             <identifier>{report_identifier}</identifier>
          </ser:getReportResultCsv>
       </soapenv:Body>
    </soapenv:Envelope>
    """

    # Send POST request to get the report results
    response = requests.post(url, data=get_report_result_soap, headers=headers)

    # Clean up the response content to remove extra information
    cleaned_content = response.content.replace(b'<?xml version=\'1.0\' encoding=\'UTF-8\'?><env:Envelope xmlns:env="http://schemas.xmlsoap.org/soap/envelope/"><env:Header/><env:Body><ns2:getReportResultCsvResponse xmlns:ns2="http://service.admin.ws.five9.com/"><return>', b'')

    # Print the report results or do further processing as needed
    if response.status_code == 200:
        return cleaned_content
    else:
        print("Failed to retrieve report results CSV:", response.text)
        return None

def main():
    # Calculate start and end timestamps for yesterday
    yesterday = datetime.now() - timedelta(days=1)
    start_timestamp = yesterday.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    end_timestamp = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999).isoformat()
    yesterdayDate = yesterday.strftime("%d_%m_%Y")

    # Define folderName and reportName combinations in a list of tuples
    folder_report_combinations = [
        ("Shared Reports", "Call Log"),
        # Add more combinations as needed
    ]

    report_identifiers = {}

    # Run reports for all folder-report combinations
    for folder_name, report_name in folder_report_combinations:
        report_identifier = run_report(folder_name, report_name, start_timestamp, end_timestamp)
        if report_identifier:
            report_identifiers[(folder_name, report_name)] = report_identifier

    # Check if reports are still running
    while any(is_report_running(report_id) for report_id in report_identifiers.values()):
        print("Reports are still running. Waiting for a minute...")
        time.sleep(60)  # Wait for a minute before checking again

    # Define the output folder
    output_folder = "/Users/bmilici/Library/CloudStorage/OneDrive-Five9/Desktop/API/Exports"

    # Get report results for all report identifiers
    for (folder_name, report_name), report_identifier in report_identifiers.items():
        report_csv_data = get_report_results_csv(report_identifier)
        if report_csv_data:
            # Construct the output file path
            output_file_path = os.path.join(output_folder, f"{report_name}_{yesterdayDate}.csv")
            with open(output_file_path, "wb") as file:
                file.write(report_csv_data)
            print(f"Report results CSV saved successfully for {folder_name} - {report_name}.")
        else:
            print(f"Failed to retrieve report results CSV for {folder_name} - {report_name}.")

if __name__ == "__main__":
    main()
