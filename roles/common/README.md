# common

This role on the server will:

01. Configure the SSH user access by loading a new `authorized_keys` file to `debian` user account.
02. Configure nameservers into the resolv.conf file.
03. Add host info to `/etc/hosts`.
04. Configure the `hostname` with the FQDN provided by the host yaml file.
05. Add ROOT user password and disable ROOT SSH Login access.
06. Manage cloud-init configuration.
07. Install needed packages.
08. Replace the default mirror with the preferred one, if provided.
09. Configure NTP service and the timezone.
10. Configure SSL in the `/etc/ssl/` directory.
11. Add/remove a SWAP file.
12. Set locale to en_US.UTF-8 if not already set.

## Requirements

If a Traditional CA is used to provide SSL credentials:

* `common_ssl_ca` has to contain the PEM CA Certificate filename inserted into: `{{ files_dir }}/{{ fqdn }}/ssl`
* `common_ssl_cert` has to contain the PEM SSL Certificate filename inserted into: `{{ files_dir }}/{{ fqdn }}/ssl`
* `common_ssl_key` has to contain the PEM SSL Private Key filename inserted into: `{{ files_dir }}/{{ fqdn }}/ssl`

To renew the SSL credentials:

1. Modify the file pointed by `common_ssl_cert`, `common_ssl_key` and `common_ssl_ca`.
2. Run the Ansible Playbook with `--tags ssl_update`.

If ACME protocol is used to provide SSL credentials:

* `common_ssl_ca_acme_email` has to be valued with ACME account email
* `common_ssl_ca_acme_url` has to be valued with ACME server URL
* `common_ssl_ca_acme_key_id` has to be valued with ACME account key ID
* `common_ssl_ca_acme_hmac` has to be valued with ACME account HMAC Key
* Only one between `common_ssl_ca_acme_rsa_size` and `common_ssl_ca_acme_elliptic_curve` has to be valued

Add the Fail2Ban configuration to:

* `roles/common/files/jail.conf`

## Role Variables

See `defaults/main.yml` to discover variables that can/should be set to use this role

## Dependencies

No dependency

## Example Playbook

```yaml
- hosts: servers
  roles:
    - role: common
      vars:
        # Machine Variables
        fqdn: idp.example.org
        files_dir: "{{ playbook_dir }}/inventories/files"

        # Traditional CA:
        #common_ssl_ca: "ca.crt"
        #common_ssl_cert: "idp.example.org.crt"
        #common_ssl_key: "idp.example.org.key"

        # ACME:
        common_ssl_ca_acme_email: "<EMAIL>"
        common_ssl_ca_acme_url: "<ACME URL>"
        common_ssl_ca_acme_key_id: "<KEY ID>"
        common_ssl_ca_acme_hmac: "<HMAC KEY>"
        common_ssl_ca_acme_rsa_size: "3072"
        #common_ssl_ca_acme_elliptic_curve: "secp384r1"

        # Add(present) or Remove(absent) SWAP file.
        # Remove entirely "swap" section if you use a dedicated partition for SWAP or if don't need it.
        common_swap_file_name: "swapfile"
        common_swap_file_size: "2048"
        common_swap_file_state: "present"

        # Remove entirely "mirror" section to use the default distribution repositories
        common_mirror_url: "http://deb.debian.org/debian/"
        common_root_user_pw: "root_password"

        # NTP
        common_ntp_timezone: Europe/Rome

        common_ntp_servers: "0.it.pool.ntp.org 1.it.pool.ntp.org 2.it.pool.ntp.org 3.it.pool.ntp.org"

        common_nameservers:
          - "1.0.0.1"
          - "1.1.1.1"
```

## License

Apache License v2.0 (January 2004)

## Author Information

Marco Malavolti (<marco.malavolti@garr.it>)
