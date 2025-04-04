import requests
import base64
import xml.etree.ElementTree as ET
import pandas as pd
import re
import os

# Define multiple Five9 API credentials with a 'region' parameter
credentials_list = [
    
   # Enter the list of users with API access below so you can create the report. 
  {"username": "test", "password": "XXXXXXX", "sheet_name": "Sheet1", "region": "com"},
  {"username": "test2", "password": "XXXXXXX", "sheet_name": "Sheet2", "region": "eu"},
]


# Define the base Five9 API URLs
api_urls = {
    "com": "https://api.five9.com:443/wsadmin/v12/AdminWebService",
    "eu": "https://api.five9.eu:443/wsadmin/v12/AdminWebService",
}

# Dictionary to store DataFrames for each account
dataframes = {}

# Loop through each credential set and fetch data
for cred in credentials_list:
    username = cred["username"]
    password = cred["password"]
    sheet_name = cred["sheet_name"]
    region = cred["region"]

    if username == "NA":
        continue

    # Determine API URL based on region
    api_url = api_urls[region]

    # Encode credentials
    credentials = base64.b64encode(f"{username}:{password}".encode()).decode()

    # Set headers with authorization
    headers = {
        "Content-Type": "text/xml;charset=UTF-8",
        "SOAPAction": "http://service.admin.ws.five9.com/getUsersInfo",
        "Authorization": f"Basic {credentials}",
    }

    # Define the SOAP request payload
    soap_envelope = """
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ser="http://service.admin.ws.five9.com/">
       <soapenv:Header/>
       <soapenv:Body>
          <ser:getUsersInfo>
             <userNamePattern>(.*)</userNamePattern>
          </ser:getUsersInfo>
       </soapenv:Body>
    </soapenv:Envelope>
    """

    # Make the API request
    response = requests.post(api_url, headers=headers, data=soap_envelope)

    if response.status_code == 200:
        # Parse the XML response
        raw_xml = response.content.decode()
        raw_xml = re.sub(r'xmlns="[^"]+"', '', raw_xml)
        raw_xml = re.sub(r'ns\d+:', '', raw_xml)

        root = ET.fromstring(raw_xml)
        users = []

        for user in root.findall(".//return"):
            user_data = {"Source Sheet": sheet_name}
            general_info = user.find("generalInfo")

            if general_info is not None:
                user_data["User ID"] = general_info.findtext("id", "")
                user_data["First Name"] = general_info.findtext("firstName", "")
                user_data["Last Name"] = general_info.findtext("lastName", "")
                user_data["Full Name"] = general_info.findtext("fullName", "")
                user_data["Email"] = general_info.findtext("EMail", "")
                user_data["Username"] = general_info.findtext("userName", "")
                user_data["Active"] = general_info.findtext("active", "")
                user_data["Can Change Password"] = general_info.findtext("canChangePassword", "")
                user_data["Federation ID"] = general_info.findtext("federationId", "")
                user_data["Extension"] = general_info.findtext("extension", "")
                user_data["Must Change Password"] = general_info.findtext("mustChangePassword", "")

            users.append(user_data)

        if users:
            df = pd.DataFrame(users)
            dataframes[sheet_name] = df
            print(f"✅ Data successfully retrieved for {sheet_name}.")
        else:
            print(f"⚠️ No users found in the response for {sheet_name}.")

    else:
        print(f"❌ Failed to retrieve agent information for {sheet_name}. Status code: {response.status_code}")

# Save all DataFrames to one Excel file, each in a different sheet
if dataframes:
    # Create a combined DataFrame for all users
    all_users_df = pd.concat(
        [df.assign(**{"Source Sheet": sheet_name}) for sheet_name, df in dataframes.items()],
        ignore_index=True,
    )

    # Move "Source Sheet" to the first column
    cols = ["Source Sheet"] + [col for col in all_users_df.columns if col != "Source Sheet"]
    all_users_df = all_users_df[cols]

    # Set output file path
    output_file = "/five9_user_info.xlsx"

    # Write all sheets to one Excel file
    with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
        for sheet_name, df in dataframes.items():
            safe_sheet_name = sheet_name[:31]
            df.to_excel(writer, sheet_name=safe_sheet_name, index=False)

        all_users_df.to_excel(writer, sheet_name="All Users", index=False)

    print(f"\n📁 All user info (including 'All Users') saved to: {os.path.abspath(output_file)}")

else:
    print("\n⚠️ No data was retrieved from any of the accounts — nothing to save.")
