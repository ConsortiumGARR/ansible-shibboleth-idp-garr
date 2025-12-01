# ANSIBLE-SHIBBOLETH-IDP-GARR

This project allows installing and configuring one or more Shibboleth Identity Providers using Ansible, following the guidelines of the IDEM GARR Federation.
The playbook enables, after an initial installation, the replacement of any file in the `shibboleth-idp` folder to restore/clone one's production IdP onto a new server.

## Table of Content

1. [Requirements](#requirements)
2. [Documentation](#documentation)
3. [Install instruction](#install-instruction)
4. [Useful Commands](#useful-commands)
5. [Tags Available](#tags-available)
6. [Host Vars](#host-vars)
7. [Authors](#authors)

## Requirements

DOC: <https://docs.ansible.com/projects/ansible/latest/reference_appendices/release_and_maintenance.html#ansible-core-support-matrix>

Version 1.0.3 tested with:

* Ansible Core 2.20.0
* Python 3.13.5 (vith 'passlib' and 'validators' libraries)
* Debian Linux 13 server for:
  * Control Node / Ansible Master
  * Remote Node / Ansible Slave:
    * Shibboleth Identity Provider v5.x

## Documentation

Inside this project you will find:

* [inventories](./inventories/README.md) directory: containing files and folders used by Ansible to know which servers to configure.
* [roles](./roles/README.md) directory: containing files and folders used by Ansible to know what operation to perform on each server.
* [scripts](./scripts/README.md) directory: Python scripts for creating new servers that make use of this Ansible project.
* Playbooks:
  * `shib-idp-servers.yml`: to install, configure and run Shibboleth Identity Providers.

The `shib-idp-servers.yml` playbook contains:

* `hosts`        (who is configured)
* `become: true` (act as ROOT user)
* `roles`        (what is installed/configured)

[[TOC](#table-of-content)]

## Install instruction

These instruction are tested on Debian 12 (bookworm):

01. Install required packages:

    * `sudo apt-get install git rsync python3-debian python3-passlib python3-pip`
    * `sudo apt-get install python3-virtualenv python3-setuptools python3-packaging`
    * `sudo apt-get install python3-validators`
    * `sudo apt-get install ansible-core --no-install-recommends`

02. Install [community.general](<https://docs.ansible.com/ansible/latest/collections/community/general/index.html>) Ansible collection (it takes several minutes):

    * `ansible-galaxy collection install community.general`

03. Install [ansible.posix](<https://docs.ansible.com/ansible/latest/collections/ansible/posix/index.html>) Ansible collection:

    * `ansible-galaxy collection install ansible.posix`

04. Download Ansible-Shibboleth-IDP-GARR project from GIT:

    * `cd $HOME ; git clone --depth 1 --branch v1.0.3 https://github.com/ConsortiumGARR/ansible-shibboleth-idp-garr.git`
    * `cd ansible-shibboleth-idp-garr ; git checkout tags/v1.0.3`

05. Create the `debian` user on the remote server to configure:

    * `useradd -U -m -s /bin/bash -u 1000 debian`
    * `cat /etc/passwd | grep debian`:
      * `debian:x:1000:1000:Debian:/home/debian:/bin/bash`

06. Copy your SSH Key into the remote `debian` user to allow SSH access without password:

    * `ssh-copy-id -i ~/.ssh/mykey debian@host`

07. Create your inventory by following the [inventories/README.md](inventories/README.md) file.

08. (OPTIONAL) Create your `.vault_pass` to contains the encryption password (this is needed ONLY when you use Ansible Vault):
    * `cd $HOME/ansible-shibboleth-idp-garr`
    * `openssl rand -base64 48 > .vault_pass`
    * `export ANSIBLE_VAULT_PASSWORD_FILE=$HOME/ansible-shibboleth-idp-garr/.vault_pass`

09. Read all [roles](./roles/README.md) README files and build your servers' host_vars files.
    An example is provided on `inventories/example/host_vars/idp.example.org.yml`.

    **PAY ATTENTION! All variables not defined and valued into the host_vars YAML file, will take the default values.**

10. Examples of ansible-playbook command used to configure the inventory hosts:

    * Execute Ansible on `example.ini` inventory and install and configure the example `idp.example.org` Identity Provider with a `demo` user:
     `ansible-playbook shib-idp-servers.yml -i inventories/example/example.ini`

      at the end of the execution check if it is working with:

      `curl https://idp.example.org/idp/shibboleth`

      or

      `/opt/shibboleth-idp/bin/aacli.sh -r https://sp.example.org/shibboleth -n demo --saml2`

    * Execute Ansible on `develoment` inventory and install and configure an IdP only on a specific server (FQDN):
     `ansible-playbook shib-idp-servers.yml -i inventories/develoment/develoment.ini --limit idp.fqdn.org --vault-password-file .vault_pass`

    * Execute Ansible on `develoment` inventory and to install and configure all IdPs into the development inventory:
     `ansible-playbook shib-idp-servers.yml -i inventories/develoment/develoment.ini`

[[TOC](#table-of-content)]

## Useful Commands

```ini
--- inventories/develoment/development.ini ---
[shib_idp]
idp.fqdn.org ansible_host=192.168.1.5 ansible_connection=ssh ansible_user=debian ansible_ssh_private_key_file=/ssh/private/key/path
```

* `GROUP_NAME = shib_idp`
* `HOST_NAME = idp.fqdn.org`

01. Test that the connection with the server(s) is working:

    `ansible all -m ping -i inventories/develoment/develoment.ini -u debian`

02. Get the facts from the server(s):

    `ansible GROUP_NAME_or_HOST_NAME -m setup -i inventories/develoment/develoment.ini -u debian`

    Examples:

    * without encrypted files:
  
      `ansible shib_idp -m setup -i inventories/develoment/develoment.ini -u debian`

    * with encrypted files:

      `ansible idp.example.org -m setup -i inventories/develoment/develoment.ini -u debian --vault-password-file .vault_pass`

      (`.vault_pass` is the file you have created that contains the encryption password)

03. Reboot all servers after 1 minute:

    `ansible all -m command -a "/sbin/shutdown -r +1" -i inventories/develoment/develoment.ini -u debian --vault-password-file .vault_pass --become`

04. Encrypt files with Ansible Vault:

    `ansible-vault encrypt inventories/develoment/host_vars/idp.fqdn.org.yml --vault-password-file .vault_pass`

05. Decrypt Encrypted files with Ansible Vault:

    `ansible-vault decrypt inventories/develoment/host_vars/idp.fqdn.org.yml --vault-password-file .vault_pass`

06. View Encrypted files with Ansible Vault:

    `ansible-vault view inventories/develoment/host_vars/idp.fqdn.org.yml --vault-password-file .vault_pass`

07. Remove Shibboleth IdP (without Ansible Vault):

    `ansible-playbook shib-idp-servers.yml -i inventories/develoment/develoment.ini --limit idp.fqdn.org --tags idp-remove`

08. Remove Apache, JDK, Jetty and Shibboleth IdP (without Ansible Vault):

    `ansible-playbook shib-idp-servers.yml -i inventories/develoment/develoment.ini --limit idp.fqdn.org --tags remove`

[[TOC](#table-of-content)]

## Tags Available

* `common`: will execute the [common](./roles/common/README.md) role.
* `ssl_update`: will update SSL credentials (Cert & Key) if Traditional CA is used.
* `apache`: will execute the [apache](./roles/apache/README.md) role.
* `apache-remove`: will remove Apache.
* `jdk`: will execute the [jdk](./roles/jdk/README.md) role.
* `jdk-remove`: will remove JDK.
* `jetty`: will execute the [jetty](./roles/jetty/README.md) role.
* `jetty-remove`: will remove Jetty.
* `idp`: will execute the [idp](./roles/idp/README.md) role
* `idp-remove`: will remove Shibboleth IdP.
* `sys-update`: will execute the [sys-update](./roles/sys-update/README.md) role
* `remove`: will remove Apache, JDK, Jetty and Shibboleth IdP.

[[TOC](#table-of-content)]

## Host Vars

| Variable                                             | Description                                                                                                                      | Default Value                                                                                       | Mandatory on Host Var YAML file                                             |   |
|------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|---|
| `fqdn`                                               | Remote Host FQDN                                                                                                                 | `idp.example.org`                                                                                   | Yes                                                                         |   |
| `files_dir`                                          | Remote Host files dir                                                                                                            | `{{ playbook_dir }}/inventories/files`                                                              | No                                                                          |   |
| `common_ssl_ca`                                      | SSL CA                                                                                                                           | `ca.crt`                                                                                            | Yes, if ACME is not used                                                    |   |
| `common_ssl_cert`                                    | SSL Certificate                                                                                                                  | `idp.example.org.crt`                                                                               | Yes, if ACME is not used                                                    |   |
| `common_ssl_key`                                     | SSL Private Key                                                                                                                  | `idp.example.org.key`                                                                               | Yes, if ACME is not used                                                    |   |
| `common_ssl_ca_acme_email`                           | SSL ACME Account e-mail                                                                                                          |                                                                                                     | Yes, if SSL CA is not used                                                  |   |
| `common_ssl_ca_acme_url`                             | SSL ACME URL                                                                                                                     |                                                                                                     | Yes, if SSL CA is not used                                                  |   |
| `common_ssl_ca_acme_key_id`                          | SSL ACME Key ID                                                                                                                  |                                                                                                     | Yes, if SSL CA is not used                                                  |   |
| `common_ssl_ca_acme_hmac`                            | SSL ACME HMAC Key                                                                                                                |                                                                                                     | Yes, if SSL CA is not used                                                  |   |
| `common_ssl_ca_acme_rsa_size`                        | SSL ACME KEY size                                                                                                                |                                                                                                     | Yes, if SSL CA and Elliptic Curve are not used                              |   |
| `common_ssl_ca_acme_elliptic_curve`                  | SSL ACME Elliptic Curve                                                                                                          |                                                                                                     | Yes, if SSL CA and RSA key are not used                                     |   |
| `common_swap_file_name`                              | SWAP file name                                                                                                                   | `swapfile`                                                                                          | No                                                                          |   |
| `common_swap_file_size`                              | SWAP file size                                                                                                                   | `2048`                                                                                              | No                                                                          |   |
| `common_swap_file_state`                             | Enable/Disable SWAP file                                                                                                         | `present`                                                                                           | No                                                                          |   |
| `common_mirror_url`                                  | Mirror URL for APT                                                                                                               | `http://deb.debian.org/debian/`                                                                     | No                                                                          |   |
| `common_root_user_pw`                                | Root user password                                                                                                               | `root_password`                                                                                     | Yes                                                                         |   |
| `common_ntp_timezone`                                | Timezone                                                                                                                         | `UTC`                                                                                               | No                                                                          |   |
| `common_ntp_servers`                                 | NTP servers                                                                                                                      | `0.it.pool.ntp.org 1.it.pool.ntp.org 2.it.pool.ntp.org 3.it.pool.ntp.org`                           | No                                                                          |   |
| `common_nameservers`                                 | DNS Nameservers                                                                                                                  | `['1.1.1.1', '1.0.0.1']`                                                                            | Yes                                                                         |   |
| `apache_admin_email`                                 | Apache admin e-mail address and IdP Technical Contact                                                                            | `root@localhost`                                                                                    | Yes                                                                         |   |
| `jdk_version`                                        | Amazon Corretto JDK version                                                                                                      | `17`                                                                                                | No                                                                          |   |
| `jetty_distribution`                                 | Jetty distribution                                                                                                               | `12.0.8`                                                                                            | No                                                                          |   |
| `jetty_logback_lib_version`                          | Logback library version                                                                                                          | `1.5.3`                                                                                             | No                                                                          |   |
| `jetty_requestlog_file`                              | Request Log file name                                                                                                            | `jetty-requestlog.xml`                                                                              | No                                                                          |   |
| `jetty_start_ini`                                    | Jetty start.ini file to use                                                                                                      | `files/java{{ jdk_version }}/start.ini`                                                             | No                                                                          |   |
| `idp_version`                                        | Shibboleth IDP version                                                                                                           | `5.1.3`                                                                                             | No                                                                          |   |
| `idp_sync`                                           | Synchronize `/opt/shibboleth-idp` content from Ansible Host to the Remote Host dir                                               | `no`                                                                                                | Yes                                                                         |   |
| `idp_entityID`                                       | entityID IdP                                                                                                                     | `https://idp.example.org/idp/shibboleth`                                                            | Yes                                                                         |   |
| `idp_scope`                                          | A string reporting one domain name belonging the institution                                                                     | `example.org`                                                                                       | Yes                                                                         |   |
| `idp_displayname`                                    | Metadata DisplayName english value                                                                                               | `Example` IdP                                                                                       | Yes                                                                         |   |
| `idp_org_url`                                        | metadata OrganizationUrl english value                                                                                           | `https://org.example.org/en`                                                                        | Yes                                                                         |   |
| `idp_technical_contact`                              | IdP Technical Contact e-mail address                                                                                             | `root@localhost`                                                                                    | Yes                                                                         |   |
| `idp_sealer_pw`                                      | sealer password                                                                                                                  | `sealer-password`                                                                                   | Yes                                                                         |   |
| `idp_keystore_pw`                                    | keystore password                                                                                                                | `keystore-password`                                                                                 | Yes                                                                         |   |
| `idp_persistentId_sourceAttribute`                   | persistent-id source attribute                                                                                                   | `uid`                                                                                               | Yes                                                                         |   |
| `idp_persistentId_salt`                              | persistent-id salt                                                                                                               | `a_random_16_chars_string`                                                                          | Yes                                                                         |   |
| `idp_persistentId_salt_encoded`                      | Enabling Base64 encoding of IdP persistent-id salt                                                                               | `true`                                                                                              |                                                                             |   |
| `idp_fticks_enabled`                                 | f-ticks activation flag                                                                                                          | `false`                                                                                             | No                                                                          |   |
| `idp_fticks_federation`                              | f-ticks federation value                                                                                                         | `MyFederation`                                                                                      | No                                                                          |   |
| `idp_fticks_condition`                               | f-ticks condition                                                                                                                |                                                                                                     | No                                                                          |   |
| `idp_fticks_algorithm`                               | f-ticks algorithm                                                                                                                | `SHA-256`                                                                                           | No                                                                          |   |
| `idp_fticks_salt`                                    | f-ticks salt                                                                                                                     |                                                                                                     | No                                                                          |   |
| `idp_fticks_loghost`                                 | f-ticks log host                                                                                                                 | `localhost`                                                                                         | No                                                                          |   |
| `idp_fticks_logport`                                 | f-ticks log port                                                                                                                 | `514`                                                                                               | No                                                                          |   |
| `idp_authn_LDAP_ldapURL`                             | Connection URI for LDAP directory.                                                                                               | `ldap://ldap.example.org`                                                                           | Yes                                                                         |   |
| `idp_authn_LDAP_baseDN`                              | Base DN to search against, used by bindSearchAuthenticator                                                                       | `ou=people,dc=ldap,dc=example,dc=org`                                                               | Yes                                                                         |   |
| `idp_authn_LDAP_bindDN`                              | DN to bind with during search, used by bindSearchAuthenticator                                                                   | `cn=idm-user,ou=system,dc=ldap,dc=example,dc=org`                                                   | Yes                                                                         |   |
| `idp_authn_LDAP_bindDNCredential`                    | Password to bind with during search, used by bindSearchAuthenticator                                                             | `ldap_user_pw`                                                                                      | Yes                                                                         |   |
| `idp_authn_LDAP_useStartTLS`                         | Enable/Disable usage of StartTLS                                                                                                 | `no`                                                                                                | No                                                                          |   |
| `idp_authn_LDAP_trustCertificates`                   | Enable/Disable usage of `/opt/shibboleth-idp/credentials/ldap-server.crt` certificateTrust.                                      | `no`                                                                                                | No                                                                          |   |
| `idp_authn_LDAP_subtreeSearch`                       | Whether to search recursively, used by bindSearchAuthenticator                                                                   | `false`                                                                                             | No                                                                          |   |
| `idp_authn_LDAP_userFilter`                          | LDAP search filter, used by bindSearchAuthenticator                                                                              | `uid={user}`                                                                                        | Yes                                                                         |   |
| `idp_authn_LDAP_usePasswordPolicy`                   | Whether to use the Password Policy Control                                                                                       | `false`                                                                                             | No                                                                          |   |
| `idp_authn_LDAP_usePasswordExpiration`               | Whether to use the Password Expired Control.                                                                                     | `false`                                                                                             | No                                                                          |   |
| `idp_attribute_resolver_LDAP_searchFilter`           | Search filter to be sent to the LDAP directory server                                                                            | `(uid=$resolutionContext.principal)`                                                                | Yes                                                                         |   |
| `idp_attribute_resolver_LDAP_exportAttributes`       | The 'exportAttributes' contains a list space-separated of attributes to retrieve directly from the directory service.            | `uid givenName sn cn mail displayName eduPersonAffiliation eduPersonEntitlement eduPersonAssurance` |                                                                             |   |
| `idp_metadata_providers['id']`                       | MetadataProvider identifier                                                                                                      | `MetadataProviderID_1`                                                                              | Yes                                                                         |   |
| `idp_metadata_providers['file']`                     | Name of the destination of the downloaded file                                                                                   | `federation-metadata.xml`                                                                           | Yes, if a metadata file is provided by URL                                  |   |
| `idp_metadata_providers['url']`                      | Metadata source URL                                                                                                              | `https://my-federation.example.org/metadata.xml`                                                    | Yes, if a metadata file is provided by URL                                  |   |
| `idp_metadata_providers['maxValidInterval']`         | Metadata ValidUntil max validation interval                                                                                      | `P10D`                                                                                              | No, set to empty value to remove it                                         |   |
| `idp_metadata_providers['disregardTLSCertificate']`  | If true, no TLS certificate checking will take place over an HTTPS connection.                                                   | `false`                                                                                             | No                                                                          |   |
| `idp_metadata_providers['pubKey']`                   | Public Key used to verify the metadata signature                                                                                 | `MIIBojAN...MBBAE= or roles/idp/files/metadata/example.pubkey`                                      | Yes                                                                         |   |
| `idp_metadata_providers['connectionRequestTimeout']` | The maximum amount of time to wait for a connection to be returned from the HTTP client's connection pool manager                | `PT2S`                                                                                              | Yes, if a metadata file is provided by MDQ                                  |   |
| `idp_metadata_providers['connectionTimeout']`        | The maximum amount of time to wait to establish a connection with the remote server.                                             | `PT2S`                                                                                              | Yes, if a metadata file is provided by MDQ                                  |   |
| `idp_metadata_providers['socketTimeout']`            | The maximum amount of time to wait between two consecutive packets while reading from the socket connected to the remote server. | `PT4S`                                                                                              | Yes, if a metadata file is provided by MDQ                                  |   |
| `idp_metadata_providers['refreshDelayFactor']`       | A factor applied to the initially determined refresh time in order to determine the next refresh time                            | `0.025`                                                                                             | Yes, if a metadata file is provided by MDQ                                  |   |
| `idp_metadata_providers['maxCacheDuration']`         | The maximum duration for which metadata will be cached before it is refreshed                                                    | `PT48H`                                                                                             | Yes, if a metadata file is provided by MDQ                                  |   |
| `idp_metadata_providers['mdQueryProtocol']`          | MDQ URL                                                                                                                          | `https://mdq.example.org/global/`                                                                   | Yes, if a metadata file is provided by MDQ. Set to empty value to remove it |   |

## Authors

### Original Authors

* Marco Malavolti (<https://github.com/malavolti>)

[[TOC](#table-of-content)]
