modcloth.sumologic-collector
===========================

This role installs and configures a Sumologic collector.

Requirements
------------

Sumologic install `.deb` for your architecture.

Role Variables
--------------

The following variables are required:
```yml
# Should be a path to a .deb file downloaded from Sumologic
# Available after account creation (click 'Add Collector' -> 'Installed Collector')
- sumologic_installer_file
```

The following variables are optional:
```yml
# Where to copy the installer to (defaults to `/tmp/sumo.deb`)
- sumologic_installer_remote_file

# Template to use for JSON sources (if defined, will be copied to server via
# `template` module and pointed to by sumo.conf)
- sumologic_collector_source_template
```

These variables are used to generate `sumo.conf` (only those present will be included):
```yml
- sumologic_collector_name
- sumologic_collector_email
- sumologic_collector_password
- sumologic_collector_accessid
- sumologic_collector_accesskey
- sumologic_collector_override
- sumologic_collector_ephemeral
- sumologic_collector_clobber
```
See: https://service.sumologic.com/help/Using_sumo.conf.htm for descriptions of values.

If `sumologic_collector_source_template` is not empty, the `sources` directive
will be added to `sumo.conf` to point to the gerenated JSON file.

See
https://service.sumologic.com/help/Default.htm#Using_JSON_to_configure_Sources.htm
for description of valid sources JSON.

You can also configure your collector via the Sumologic UI.

Dependencies
------------

None.

Example Playbook
----------------

```yml
- hosts: servers
  roles:
  - role: modcloth.sumologic-collector
    sumologic_installer_file: files/sumocollector_19.99-1_amd64.deb
    sumologic_collector_source_template: templates/sumo-sources.json.j2
    sumologic_collector_accessid: 'foo'
    sumologic_collector_accesskey: 'bar'
    sumologic_collector_override: 'true'
```

License
-------

MIT

Author Information
------------------

Modcloth, Inc.
