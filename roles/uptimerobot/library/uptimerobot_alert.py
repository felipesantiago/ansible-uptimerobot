#!/usr/bin/python

import urllib
from ansible.module_utils.request_cache import RequestCache
from ansible.module_utils.basic import AnsibleModule

CACHE_TIMEOUT = 300
API_KEY = ''
API_BASE = 'https://api.uptimerobot.com/v2/'
API_ACTIONS = dict(
    new='newAlertContact',
    getid='getAlertContacts',
    delete='deleteAlertContact'
)

def callApi(status, data={}):
    api_url = API_BASE + API_ACTIONS[status]
    base_payload = {
        'api_key': API_KEY,
        'format': 'json'
    }
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'cache-control': 'no-cache'
    }

    payload = dict(base_payload, **data)
    return request_cache.request('POST', api_url, payload, headers)

def getAlertContactID(value):
    getid = callApi('getid')
    contactlist = getid['total']

    for getcontactid in range(contactlist):
        if getid['alert_contacts'][getcontactid]['value'] == value:
            return getid['alert_contacts'][getcontactid]['id']

def newAlertContact(alert_type, alert_name, value, status):
    payload = {
        'type': alert_type,
        'friendly_name': urllib.quote_plus(alert_name),
        'value': value,
        'status': status
    }
    newalert = callApi('new', payload)

    if newalert['stat'] == 'ok':
        return 'ok'
    else:
        return newalert['error']['message']

def deleteAlertContact(value):
    contact_value = getAlertContactID(value)
    if contact_value is not None:
        id = '%s' % contact_value
    else:
        return 'Contact id not found'

    payload = {
        'id': id
    }
    result = callApi('delete', payload)

    if result['stat'] == 'ok':
        return 'ok'
    else:
        return result['error']['message']


def main(module):
    alert_name = module.params['alert_name']
    state = module.params['state']
    status = module.params['status']
    alert_type = module.params['alert_type']
    value = module.params['value']

    if state == 'present':
        result = newAlertContact(alert_type, alert_name, value, status)
        if result == 'ok':
            module.exit_json(changed=True, name=alert_name, state=state)
        elif result == 'Alert Contact already exists.':
            module.exit_json(changed=False, msg='Alert Contact %s already exists.' % alert_name)
        else:
            module.fail_json(msg= '%s' % result)

    elif state == 'absent':
        result = deleteAlertContact(value)
        if result == 'ok':
            module.exit_json(changed=True, alert_name=alert_name, value=value, state=state)
        elif result == 'Contact id not found':
            module.exit_json(msg='Not removed, reason: %s' % result)
        else:
            module.fail_json(msg='%s' % result)

    else:
        module.fail_json(msg='invalid state')

if __name__ == '__main__':
    request_cache = RequestCache(cache_time=CACHE_TIMEOUT)
    module = AnsibleModule(
        argument_spec=dict(
            api_key=dict(type='str', required=True),
            alert_name=dict(type='str', required=True),
            state=dict(required=True, choices=['present', 'absent']),
            status=dict(type='str', required=True),
            alert_type=dict(type='str', required=True),
            value=dict(type='str', required=True)
        )
    )

    API_KEY = module.params['api_key']
    main(module)