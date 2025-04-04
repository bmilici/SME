import requests
import base64
import xml.etree.ElementTree as ET

# Define your Five9 API credentials
username = ""
password = ""

# Encode the credentials
credentials = base64.b64encode(f"{username}:{password}".encode()).decode()

# Define the URL of the SOAP API
url = "https://api.five9.com:443/wsadmin/v12/AdminWebService"

# List of skills to be deleted
skills = [
    "Skill1", "Skill2", "Skill3"
]

# Loop through the skills and delete each one
for skill in skills:
    # Define the SOAP envelope with the deleteSkill request for each skill
    soap_envelope = f"""
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ser="http://service.admin.ws.five9.com/">
       <soapenv:Header/>
       <soapenv:Body>
          <ser:deleteSkill>
             <skillName>{skill}</skillName>
          </ser:deleteSkill>
       </soapenv:Body>
    </soapenv:Envelope>
    """

    # Define headers with Content-Type and Authorization
    headers = {
        "Content-Type": "text/xml;charset=UTF-8",
        "SOAPAction": "http://service.admin.ws.five9.com/deleteSkill",
        "Authorization": f"Basic {credentials}"
    }

    # Make the SOAP request
    response = requests.post(url, data=soap_envelope, headers=headers)

    # Parse the response XML
    response_xml = ET.fromstring(response.content)

    # Check for a success element or error element in the response
    if response.status_code == 200:
        success_element = response_xml.find('.//return')
        if success_element is not None and success_element.text == "true":
            print(f"Skill '{skill}' has been successfully deleted.")
        else:
            print(f"Skill '{skill}' deletion failed or was not confirmed by the response.")
    else:
        print(f"Request for skill '{skill}' failed with status code: {response.status_code}")
