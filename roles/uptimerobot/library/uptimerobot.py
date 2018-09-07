#!/usr/bin/python

from ansible.module_utils.request_cache import RequestCache
from ansible.module_utils.basic import AnsibleModule

# Time in seconds
CACHE_TIMEOUT = 300
API_KEY = ''
API_BASE = 'https://api.uptimerobot.com/v2/'
API_ACTIONS = dict(
    status='getMonitors',
    edit='editMonitor',
    new='newMonitor',
    delete='deleteMonitor'
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

def getMonitorID(url):
    monitors = callApi('status')
    monitor = next((m for m in monitors['monitors'] if m['url'] == url), None)

    if monitor is not None:
        return '%d' % monitor['id']

def newMonitor(url, name, alert_contacts):
    payload = {
        'type': 1,
        'url': url,
        'friendly_name': name
    }

    if alert_contacts is not None:
        payload['alert_contacts'] = alert_contacts

    newmonitor = callApi('new', payload)
    if newmonitor['stat'] == 'ok':
        return 'ok'
    elif newmonitor['stat'] == 'fail':
        if newmonitor['error']['type'] == 'already_exists':
            return 'monitor already exists.'

# Delete is functional, but needs more fine tunning and testing
def deleteMonitor(url):
    id = getMonitorID(url)
    if id is None:
        return 'monitor id not found'

    payload = {
        'id': id
    }

    resultmonitor = callApi('delete', payload)
    # Invalidate cache to avoid false positives
    request_cache.clear()
    if resultmonitor['stat'] == 'ok':
        return 'ok'

    return resultmonitor['error']['message']

def pauseMonitor(url):
    id = getMonitorID(url)
    if id is None:
        return 'monitor id not found'

    payload = {
        'id': id,
        'status': 0
    }

    resultmonitor = callApi('edit', payload)
    if resultmonitor['stat'] == 'ok':
        return 'ok'

    return resultmonitor['error']['message']

def startMonitor(url):
    id = getMonitorID(url)
    if id is None:
        return 'monitor id not found'

    payload = {
        'id': id,
        'status': 1
    }

    resultmonitor = callApi('edit', payload)
    if resultmonitor['stat'] == 'ok':
        return 'ok'

    return resultmonitor['error']['message']

def main(module):
    alert_contacts = module.params['alert_contacts']
    name = module.params['name']
    state = module.params['state']
    url = module.params['url']

    if state == 'present':
        result = newMonitor(url, name, alert_contacts)
        if result == 'ok':
            module.exit_json(changed=True, name=name, url=url, state=state)
        elif result == 'monitor already exists.':
            module.exit_json(changed=False, msg='monitor %s already exists.' % name)
        else:
            module.fail_json(msg='%s' % result)
    elif state == 'absent':
        result = deleteMonitor(url)
        if result == 'ok':
            module.exit_json(changed=True, msg='%s' % getMonitorID(url), name=name, url=url, state=state,)
        elif result == 'monitor id not found':
            module.exit_json(changed=False, msg='%s NOT REMOVED. reason: cannot find monitor id' % name)
        else:
            module.fail_json(msg='%s' % result)
    elif state == 'started':
        result = startMonitor(url)
        if result == 'ok':
            module.exit_json(changed=True, name=name, url=url, state=state)
        else:
            module.fail_json(msg='%s' % result)
    elif state == 'paused':
        result = pauseMonitor(url)
        if result == 'ok':
            module.exit_json(changed=True, name=name, url=url, state=state)
        else:
            module.fail_json(msg= '%s' % result)
    else:
        module.fail_json(msg='invalid state')

if __name__ == '__main__':
    request_cache = RequestCache(cache_time=CACHE_TIMEOUT)

    module = AnsibleModule(
        argument_spec=dict(
            alert_contacts=dict(type='str', required=False),
            api_key=dict(type='str', required=True),
            name=dict(type='str', required=True),
            state=dict(required=True, choices=['present', 'absent', 'started', 'paused']),
            url=dict(type='str', required=True)
        )
    )

    API_KEY = module.params['api_key']
    main(module)

