import requests
from vipconfig import apikey
 
def main():
 
    API_Secret_Key = apikey['secret_key']
    header = {'authorization': 'auth_api_secretkey=' + API_Secret_Key + ''}
 
    #Read the file with the VIP names and
    try:
        file_name = input("Enter the file name which contains the VIP List: ").strip()
        with open("./"+file_name, "r") as fileObj:
            vip_list = fileObj.readlines()
            fileObj.close()
    except Exception as e:
        print(e)
 
    for vip in vip_list:
        #Get each VIP  Name from the List and pass it to the  the GET method
        r = requests.get("https://netgenie.corp.company.net/ltmapi/v1/virtualserver?vsName="+vip.rstrip()+"-vs_tcp443", headers=header)
#        r = requests.get("https://netgenie.corp.company.net/ltmapi/v1/virtualserver?vsName="+vip.rstrip(), headers=header)
        json_obj = r.json()
        print(json_obj)
        #exit()
 
        # Converting the output in to JSON Object and storing it ina  variable
        json_obj = r.json()
 
        # Getting the status code and storing in a variable
        status = r.status_code
 
        # Extract the original JSON data to get teh LTM Type
        ltm_type = json_obj["ltm_type"].lower()
 
 
        # Extract the VIP Name and Id
        vServer = json_obj['virtual_server']
 
        #Check whether the VIP is Internal or External
        vip_ip = json_obj["virtual_server_config"]["destination"]
        tls_profile = getTLSProfile(vip_ip)
 
 
        if status == 200:
            if ltm_type == "f5":
                # Extracting the Virtual Server Profile to get the SSL Profile and storing it in variable
                ssl_profile = json_obj["virtual_server_profiles"][0]["parent_profile"].split("/")
                # Getting the last element from the List
                ssl_profile_name = ssl_profile[len(ssl_profile) - 1]
 
                profile_type = "ssl client profile"
 
                profile_name = json_obj["virtual_server_profiles"][0]["profile_name"]
 
                parent_profile = "/Common/"+tls_profile+""
 
            elif ltm_type == "avi":
                # Extracting the Virtual Server Profile to get the SSL Profile and storing it in variable
                #ssl_profile_name = json_obj["ssl_parent_profile"]
                ssl_profile_name = json_obj["virtual_server_profiles"][1]["profile_name"]
 
                profile_type = "SSL PROFILE"
 
                profile_name = tls_profile
 
                parent_profile = tls_profile
 
            else:
                print("Unknown VIP")
                break
 
            #Comparing if the SSL Profile name is old
            if ssl_profile_name != tls_profile:
                print("You are running older Chiper Profile for the VIP: {}, you need to update to TLS 1.2 Profile only setting".format(vServer))
                print("Going to update this VIP: {} with the new TLS 1.2 Profile".format(vServer))
                json_data = formatRequestData(vServer, profile_type, profile_name, parent_profile)
                output = updateVip(json_data, header)
                print(output)
            else:
                print("You are already running the latest TLS 1.2 Profile on {} ..You are Good".format(vServer))
        else:
            print("Error in getting the VIP details for {}".format(vip))
 
#Function to create teh JSON data based on the VIP Type
def formatRequestData(vServer, profile_type, profile_name="Company-standard_tls_internal", parent_profile="Company-standard_tls_internal"):
    json_update = {
        "virtual_server": vServer,
        "virtual_server_profiles": [{
            "profile_type": profile_type,
            "profile_name": profile_name,
            "parent_profile": parent_profile
        }]
    }
    return json_update
 
# Check whether the VIP is Internal or External
def getTLSProfile(vip_ip):
    destination = vip_ip.split("%")
    vServer_ip = destination[0].split(".")
    vServer_ip_first_oct = int(vServer_ip[0])
 
    if vServer_ip_first_oct == 10:
        tls_profile = "Company-standard_tls_internal"
    else:
        tls_profile = "Company-standard_tls_external"
    return tls_profile
 
#Function to update the VIP
def updateVip(json_data, header):
    u = requests.put("https://netgenie.corp.company.net/ltmapi/v1/virtualserver/",json=json_data, headers=header)
    return u.text
 
 
if __name__== "__main__":
  main()
 
