import requests
import base64

# Define your Five9 API credentials
username = ""
password = "!"

# Encode the credentials
credentials = base64.b64encode(f"{username}:{password}".encode()).decode()

# Define the URL of the SOAP API
url = "https://api.five9.com:443/wsadmin/v12/AdminWebService"

# Define headers with Content-Type and Authorization
headers = {
    "Content-Type": "text/xml;charset=UTF-8",
    # Adjust SOAPAction to match the getCampaignProfiles request
    "SOAPAction": "http://service.admin.ws.five9.com/getCampaignProfiles",
    "Authorization": f"Basic {credentials}"
}

# Define the SOAP envelope with the getCampaignProfiles request
soap_envelope = f"""
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ser="http://service.admin.ws.five9.com/">
   <soapenv:Header/>
   <soapenv:Body>
      <ser:getInboundCampaign>
         <campaignName></campaignName>
      </ser:getInboundCampaign>
   </soapenv:Body>
</soapenv:Envelope>
"""

# Make the API request
response = requests.post(url, headers=headers, data=soap_envelope)

# Check if the request was successful
if response.status_code == 200:
    # Print the raw XML response content
    print(response.text)  # Decode from bytes to string
else:
    print(f"Failed to retrieve campaign profiles. Status code: {response.status_code}")
    print(f"Response: {response.text}")

