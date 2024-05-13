# apache

This role on the server will:

01. Install Apache and the needed packages.
02. Enable Apache modules: alias, ssl, include, negotiation, headers and proxy.
03. Enable a Virtualhost with a permanent SSL redirection. (A+ on [SSLLabs](https://www.ssllabs.com/ssltest))
04. Disable the `000-default.conf` Apache site configuration.
05. Enable Apache Localized error pages.
06. Restart Apache if CA, CRT or KEY change.

## Requirements

No

## Role Variables

See `defaults/main.yml` to discover variables that can/should be set to use this role

## Dependencies

- [common](../common/README.md)

## Example Playbook

```yaml
- hosts: servers
  roles:
    - role: common
      vars: 
        # 'common' role vars.
    - role: apache
      vars:
        apache_admin_email: "root@localhost"
```

## License

Apache License v2.0 (January 2004)

## Author Information

Marco Malavolti (<marco.malavolti@garr.it>)
