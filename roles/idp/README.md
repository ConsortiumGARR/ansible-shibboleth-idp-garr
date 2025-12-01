# idp

This role on the server will:

01. Download and Install Shibboleth IdP by checking the PGP Signature
02. Install Nashorn JavaScript engine
03. Configure Shibboleth IdP LDAP connection with a Traditional CA certificate or ldap-server.crt
04. Configure Metadata Providers
05. Add 'eduPersonTargetedID' to Attribute Registry
06. Configure the script to securing cookies and other IdP data
07. Configure Apache to redirect requests to the Shibboleth IdP
08. Enable Shibboleth IdP reloadable services by CLI
09. Configure conf/relying-party.xml to enable the Attribute Release Module
10. Configure 'saml-nameid.properties'
11. Configure 'idp.properties'
12. Load the 'attribute-filter.xml' for custom filters as static file
13. Configure 'attribute-resolver.xml'
14. Configure 'logback.xml'

## Requirements

The first time the playbook is run, the `idp_sync` variable must be configured to `no` to allow the complete installation of the Shibboleth Identity Provider with all its files and folders.
Once the installation has been successfully completed, it is possible to place all desired files to replace within the Identity Provider in `files/{{ fqdn}}/shibboleth-idp`, change the value of `idp_sync` to `yes`, and run the playbook again.

To add new rules inside the `attribute-filter.xml` file configured on the IdP, simply modify the file `roles/idp/files/conf/attribute-filter.xml` or through the replacement mechanism of `idp_sync: 'yes'`.

If StartTLS or SSL is needed to connect to LDAP directory service, the file `{files_dir}/{fqdn}/shibboleth-idp/credentials/ldap-server.crt` must contains the certificate needed to establish the connection.

## Role Variables

See `defaults/main.yml` to discover variables that can/should be set to use this role.

## Dependencies

- [common](../common/README.md)
- [apache](../apache/README.md)
- [jdk](../jdk/README.md)
- [jetty](../jetty/README.md)

## Example Playbook

```yaml
- hosts: servers
  roles:
    - role: common
      vars:
        # 'common' role vars.
    - role: apache
      vars:
        # 'apache' role vars.
    - role: jdk
      vars:
        # 'jdk' role vars.
    - role: jetty
      vars:
        # 'jetty' role vars.
    - role: idp
      vars:
        idp_version: "5.1.3"
        idp_sync: "no"
        idp_entityID: "https://idp.example.org/idp/shibboleth"
        idp_scope: "example.org"
        idp_displayname: "Example IdP"
        idp_org_url: "https://org.example.org/en"
        idp_sealer_pw: "sealer-password"
        idp_keystore_pw: "keystore-password"
        idp_persistentId_sourceAttribute: "uid"
        idp_persistentId_salt: "aRandomString"
        idp_persistentId_salt_encoded: "true"
        idp_fticks_enabled: "false"
        idp_fticks_federation: "MyFederation"
        idp_fticks_condition: ""
        idp_fticks_algorithm: "SHA-256"
        idp_fticks_salt: ""
        idp_fticks_loghost: "localhost"
        idp_fticks_logport: "514"
        idp_authn_LDAP_ldapURL: "ldap://ldap.example.org"
        idp_authn_LDAP_baseDN: "ou=people,dc=ldap,dc=example,dc=org"
        idp_authn_LDAP_bindDN: "cn=idm-user,ou=system,dc=ldap,dc=example,dc=org"
        idp_authn_LDAP_bindDNCredential: "ldap_user_pw"
        idp_authn_LDAP_trustCertificates: "true"
        idp_authn_LDAP_subtreeSearch: "false"
        idp_authn_LDAP_userFilter: "uid={user}"
        idp_authn_LDAP_usePasswordPolicy: "false"
        idp_authn_LDAP_usePasswordExpiration: "false"
        idp_attribute_resolver_LDAP_searchFilter: "(uid=$resolutionContext.principal)"
        idp_metadata_providers:
          - id: "MetadataProviderID_MDQ"
            connectionRequestTimeout: "PT2S"
            connectionTimeout: "PT2S"
            socketTimeout: "PT4S"
            refreshDelayFactor: "0.025"
            maxCacheDuration: "PT48H"
            mdQueryProtocol: "https://mdq.example.org/global/"
            pubKey: |
              MIIBojANBgkqhkiG9w0BAQEFAAOCAY8AMIIBigKCAYEA32nIKnrjRK7Ib+bpKKft
              iUw7/wte3bVAoYfEg6767QnnZrF4yT0VPygAHCRdM0No2zvXtOpH8oKpJgwSdpes
              C2F6EK7MiplSD2Y2LrKhJOeFUvYgKjOb2vsiGRmv5IxHPrrkJOW61pma9t8CobBv
              i2LC3SZRWTA4Vgazp8GJDk+y2MPJRIOF7EOVeB35czY8aTHVeh195UReNf4cuUKk
              kJMcJXqQPl00PT8eFiC3R/VJOtgqSuhEPBI00VvOSC7mgRuuzLIrZVPe41vtTHj3
              +z+7DRgOu/3dFB65WS8v/EKWlwWm3vYBim9BdNMOZuKSQB/xN53OHNP2ZKcV1M+a
              gu0yULbPRQxURmoDKhE+Tp0WTv9Hy18xzmFBoaq5Rt+30cPgn3SPbNekguE5K3Am
              7GX9rw0Q+Wkyks1QRQvpdl7NhEJRInvZe2Xl0LR1Bl6bBmPVx2Qbcu5ZuDGYYq3s
              dhP/0UGOwHUWnIllq7lx5+FdVH6DVdLeFVJh5LCbNO+rAgMBBAE=
```

## License

Apache License v2.0 (January 2004)

## Author Information

Marco Malavolti (<marco.malavolti@garr.it>)
