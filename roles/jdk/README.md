# jdk

This role on the server will:

01. Install Amazon Corretto JDK

## Requirements

No

## Role Variables

See `defaults/main.yml` to discover variables that can/should be set to use this role

## Dependencies

No

## Example Playbook

```yaml
- hosts: servers
  roles:
    - role: jdk
      vars:
        jdk_version: "17"
```

## License

Apache License v2.0 (January 2004)

## Author Information

Marco Malavolti (<marco.malavolti@garr.it>)  
