#!/usr/bin/python

import requests, json
from ansible.module_utils.basic import AnsibleModule

API_BASE = "https://api.uptimerobot.com/v2/"

API_ACTIONS = dict(
    status='getMonitors',
    edit='editMonitor',
    new='newMonitor',
    delete='deleteMonitor'
)

def main():
    arg_spec = dict(
        alert_contacts=dict(type='str', required=False),
        api_key=dict(type='str', required=True),
        name=dict(type='str', required=True),
        state=dict(required=True, choices=['present', 'absent', "started", 'paused']),
        url=dict(type='str', required=True)
    )
 
    module = AnsibleModule(argument_spec=arg_spec)

    alert_contacts = module.params['alert_contacts']
    api_key = module.params['api_key']
    name = module.params['name']
    state = module.params['state']
    url = module.params['url']

    def getMonitorID():
        api_url = API_BASE + API_ACTIONS['status']
        payload = "api_key=" + api_key + "&format=json&logs=1"
    
        headers = {
            'content-type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache"
        }

        response = requests.request("POST", api_url, data=payload, headers=headers)
        getmonitor = json.loads(response.text)

        monitorlist = getmonitor['pagination']['total']

        for getmonitorid in range(monitorlist):
            if getmonitor['monitors'][getmonitorid]['url'] == url:           
                return getmonitor['monitors'][getmonitorid]['id']

    def newMonitor():
        api_url = API_BASE + API_ACTIONS['new']

        if alert_contacts is not None:
            payload = "api_key=" + api_key + "&format=json&type=1&url=" + url + "&friendly_name=" + name + "&alert_contacts=" + alert_contacts
        else:
            payload = "api_key=" + api_key + "&format=json&type=1&url=" + url + "&friendly_name=" + name
            
        headers = {
            'content-type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache"
        }

        response = requests.request("POST", api_url, data=payload, headers=headers)
        newmonitor = json.loads(response.text)
        
        if newmonitor['stat'] == "ok":        
            return "ok"
        elif newmonitor['stat'] == "fail":
            if newmonitor['error']['type'] == "already_exists":
                return "monitor already exists."


    # Delete is functional, but needs more fine tunning and testing
    def deleteMonitor():
        api_url = API_BASE + API_ACTIONS['delete']
        
        if getMonitorID() is not None:
            id = "%d" % getMonitorID()
        else:
            return "monitor id not found"

        payload = "api_key=" + api_key + "&format=json&id=" + id
    
        headers = {
            'content-type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache"
        }

        response = requests.request("POST", api_url, data=payload, headers=headers)
        resultmonitor = json.loads(response.text)

        if resultmonitor['stat'] == "ok":        
            return "ok"
        else:
            return resultmonitor['error']['message']

    def pauseMonitor():
        api_url = API_BASE + API_ACTIONS['edit']

        if getMonitorID() is not None:
            id = "%d" % getMonitorID()
        else:
            return "monitor id not found"

        payload = "api_key=" + api_key + "&format=json&id=" + id + "&status=0"
            
        headers = {
            'content-type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache"
        }

        response = requests.request("POST", api_url, data=payload, headers=headers)
        resultmonitor = json.loads(response.text)

        if resultmonitor['stat'] == "ok":        
            return "ok"
        else:
            return resultmonitor['error']['message']

    def startMonitor():
        api_url = API_BASE + API_ACTIONS['edit']

        if getMonitorID() is not None:
            id = "%d" % getMonitorID()
        else:
            return "monitor id not found"

        payload = "api_key=" + api_key + "&format=json&id=" + id + "&status=1"
            
        headers = {
            'content-type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache"
        }

        response = requests.request("POST", api_url, data=payload, headers=headers)
        resultmonitor = json.loads(response.text)

        if resultmonitor['stat'] == "ok":        
            return "ok"
        else:
            return resultmonitor['error']['message']        

    if state == 'present':
        if newMonitor() == "ok":
            module.exit_json(changed=True, name=name, url=url, state=state)
        elif newMonitor() == "monitor already exists.":
            module.exit_json(changed=False, msg="monitor %s already exists." % name)
        else:        
            module.fail_json(msg="%s" % newMonitor())

    elif state == "absent":
        if deleteMonitor() == "ok":
            module.exit_json(changed=True, msg="%s" % getMonitorID(), name=name, url=url, state=state,)
        elif deleteMonitor() == "monitor id not found":
            module.exit_json(changed=False, msg="%s NOT REMOVED. reason: cannot find monitor id" % name)
        else:        
            module.fail_json(msg="%s" % deleteMonitor())

    elif state == "started":
        if startMonitor() == "ok":
            module.exit_json(changed=True, name=name, url=url, state=state)
        else:        
            module.fail_json(msg="%s" % startMonitor())

    elif state == "paused":
        if pauseMonitor() == "ok":
            module.exit_json(changed=True, name=name, url=url, state=state)
        else:        
            module.fail_json(msg= "%s" % pauseMonitor())

    else:
        module.fail_json(msg="invalid state")

if __name__ == '__main__':
    main()

