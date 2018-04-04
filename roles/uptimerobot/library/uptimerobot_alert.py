#!/usr/bin/python

import requests, json, urllib
from ansible.module_utils.basic import AnsibleModule

API_BASE = "https://api.uptimerobot.com/v2/"

API_ACTIONS = dict(
    new='newAlertContact',
    getid='getAlertContacts',
    delete='deleteAlertContact'
)

def main():
    arg_spec = dict(
        api_key=dict(type='str', required=True),
        alert_name=dict(type='str', required=True),
        state=dict(required=True, choices=['present', 'absent']),
        status=dict(type='str', required=True),
        alert_type=dict(type='str', required=True),
        value=dict(type='str', required=True)
    )

    module = AnsibleModule(argument_spec=arg_spec)

    api_key = module.params['api_key']
    alert_name = module.params['alert_name']
    state = module.params['state']
    status = module.params['status']
    alert_type = module.params['alert_type']
    value = module.params['value']

    def getAlertContactID():
        api_url = API_BASE + API_ACTIONS['getid']
        payload = "api_key=" + api_key + "&format=json"

        headers = {
            'content-type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache"
        }

        response = requests.request("POST", api_url, data=payload, headers=headers)
        getid = json.loads(response.text)

        contactlist = getid['total']

        for getcontactid in range(contactlist):
            if getid['alert_contacts'][getcontactid]['value'] == value:
                return getid['alert_contacts'][getcontactid]['id']

    def newAlertContact():

        api_url = API_BASE + API_ACTIONS['new']

        payload = "api_key=" + api_key + "&format=json&type=" + alert_type + "&friendly_name=" + urllib.quote_plus(alert_name) + "&value=" + urllib.quote_plus(value) + "&status=" + status

        headers = {
            'content-type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache"
        }

        response = requests.request("POST", api_url, data=payload, headers=headers)
        newalert = json.loads(response.text)
        
        if newalert['stat'] == "ok":        
            return "ok"
        else:
            return newalert['error']['message']

    def deleteAlertContact():
        api_url = API_BASE + API_ACTIONS['delete']

        if getAlertContactID() is not None:
            id = "%s" % getAlertContactID()
        else:
            return "Contact id not found"

        payload = "api_key=" + api_key + "&format=json&id=" + id

        headers = {
            'content-type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache"
        }

        response = requests.request("POST", api_url, data=payload, headers=headers)
        result = json.loads(response.text)

        if result['stat'] == "ok":
            return "ok"
        else:
            return result['error']['message']

    if state == 'present':
        if newAlertContact() == "ok":
            module.exit_json(changed=True, name=alert_name, state=state)
        elif newAlertContact() == "Alert Contact already exists.":
            module.exit_json(changed=False, msg="Alert Contact %s already exists." % alert_name)
        else:
            module.fail_json(msg= "%s" % newAlertContact())

    elif state == "absent":
        if deleteAlertContact() == "ok":
            module.exit_json(changed=True, alert_name=alert_name, value=value, state=state)
        elif deleteAlertContact() == "Contact id not found":
            module.exit_json(msg="Not removed, reason: %s" % deleteAlertContact())
        else:
            module.fail_json(msg="%s" % deleteAlertContact())

    else:
        module.fail_json(msg="invalid state")

if __name__ == '__main__':
    main()