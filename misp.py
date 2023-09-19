import requests

import requests

def get_misp_ips(misp_server, misp_auth_key, event_id, ioc_type, page=1, limit=100):
    misp_url = f"https://{misp_server}/attributes/restSearch"
    headers = {
        'Authorization': misp_auth_key,
        'Cache-Control': 'no-cache',
        'Accept': 'application/json',
        'Content-type': 'application/json'
    }
    # Constructing the search parameters
    data = {
        "request": {
            "eventid": event_id,
            "type": ioc_type,
            "page": page,
            "limit": limit
        }
    }
    response = requests.post(misp_url, headers=headers, json=data, verify=False)
    response.raise_for_status()
    json_data = response.json()

    ioc_list = []
    for data in json_data["response"]["Attribute"]:
        iocs = data['value']
        ioc_list.append(iocs)

    return ioc_list



def check_ref_set(qradar_server, qradar_auth_key, qradar_ref_set):
    check_ref_set_url = f"https://{qradar_server}/api/reference_data/sets/{qradar_ref_set}"
    headers = {
        'sec': qradar_auth_key,
        'Version': '13.0'
    }
    response = requests.get(check_ref_set_url, headers=headers, verify=False)
    return response.status_code == 200

def create_ref_set(qradar_server, qradar_auth_key, qradar_ref_set):
    url = f"https://{qradar_server}/api/reference_data/sets"
    params = {"element_type": "ALNIC", "name": qradar_ref_set}
    headers = {
        "Version": "19.0",
        "Accept": "application/json",
        "SEC": qradar_auth_key
    }
    response = requests.post(url, headers=headers, params=params, verify=False)
    response.raise_for_status()
    return response.json()

def post_iocs_to_qradar(qradar_server, qradar_auth_key, qradar_ref_set, ioc_list):
    post_url = f"https://{qradar_server}/api/reference_data/sets/bulk_load/{qradar_ref_set}"
    headers = {
        'sec': qradar_auth_key,
        'content-type': "application/json",
        'Version': '13.0'
    }
    response = requests.post(post_url, json=ioc_list, headers=headers, verify=False)
    response.raise_for_status()

