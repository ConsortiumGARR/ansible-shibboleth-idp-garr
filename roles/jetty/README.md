# jetty

This role on the server will:

01. Install Jetty and Enable logging-logback as suggested by the Shibboleth Consortium

## Requirements

No

## Role Variables

See `defaults/main.yml` to discover variables that can/should be set to use this role

## Dependencies

- [jdk](../jdk/README.md)

## Example Playbook

```yaml
- hosts: servers
  roles:
    - role: jetty
```

## License

Apache License v2.0 (January 2004)

## Author Information

Marco Malavolti (<marco.malavolti@garr.it>)
