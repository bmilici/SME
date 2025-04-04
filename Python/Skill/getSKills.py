import requests
import base64
import xml.etree.ElementTree as ET

# Credentials
username = ""
password = ""
credentials = base64.b64encode(f"{username}:{password}".encode()).decode()

# SOAP API endpoint
url = "https://api.five9.com:443/wsadmin/v12/AdminWebService"
headers = {
    "Content-Type": "text/xml;charset=UTF-8",
    "SOAPAction": "http://service.admin.ws.five9.com/getCallVariables",
    "Authorization": f"Basic {credentials}"
}

# SOAP envelope
soap_envelope = f"""
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ser="http://service.admin.ws.five9.com/">
   <soapenv:Header/>
   <soapenv:Body>
      <ser:getCallVariables>
         <namePattern>.*</namePattern>
      </ser:getCallVariables>
   </soapenv:Body>
</soapenv:Envelope>
"""

# Make the request
response = requests.post(url, headers=headers, data=soap_envelope)

if response.status_code == 200:
    root = ET.fromstring(response.content)
    call_vars = root.findall(".//return")

    for var in call_vars:
        restrictions = var.findall("restrictions")
        has_set_type = any(r.findtext("type", "").lower() == "set" for r in restrictions)

        if has_set_type:
            group = var.findtext("group", default="")
            name = var.findtext("name", default="")
            var_type = var.findtext("type", default="")
            print(f"Group: {group}, Name: {name}, Type: {var_type}")
else:
    print(f"Failed with status code {response.status_code}")
    print(response.content.decode())
