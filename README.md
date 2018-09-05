# Ansible uptimerobot module


Add/remove sites to uptimerobot service.

Ansible's official module currently only supports `start`and `pause`.


## Configuration exemple:

Change your `group_vars/all/uptimerobot.yml`:

### Manage monitors:

```yaml
uptimerobot_targets:
  - { name: "Google", url: "https://gogole.com", state: "present"}
  - { name: "Slashdot", url: "https://slashdot.org", state: "present"}
```

### Manage Alert contacts:

```yaml
uptimerobot_alert_entries:
  - { alert_name: "Slack",  alert_type: "11", status: "2", value: "https://hooks.slack.com/services/XXXXXXXXX/XXXXXXXXXXXXXXXXXXXXXXXXX", state: "present" }
```

See [uptimerobot API documentation](https://uptimerobot.com/api) for more details

**Important:** _ansible-vault_ is highly recommended to store your _uptimerobot_api_key_.

```bash
$ ansible-vault encrypt group_vars/all/uptimerobot_api_key.yml
```

## Running

```bash
$ ansible-playbook main.yml --vault-pass your_vault_pass_file
```

## TODO

- [x] Add alert support for monitors
- [x] Alert management support
- [ ] Public pages support
- [ ] Maintenance windows support
- [ ] Ansible check mode support
