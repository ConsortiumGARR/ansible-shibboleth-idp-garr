# ANSIBLE-SHIBBOLETH-IDP-GARR Inventories

Several environments can be created from `inventories/examples` in the following way:

1. Development:
   * `cp inventories/example inventories/development`
2. Production:
   * `cp inventories/example inventories/production`
3. Staging:
   * `cp inventories/example inventories/staging`
4. Test:
   * `cp inventories/example inventories/test`

Inside the `inventories/` folder are stored all the files and folders needed by Ansible to configure the remote servers.
Files and/or folders containing the word `example` are templates to be adapted as needed:

* `example/group_vars/all.yml`:

  file containing variables shared to all servers controlled with Ansible.
* `example/host_vars/idp.example.org.yml`:

  template file containing the variables used by a specific host.

  Copy this file to a new file whose name carries the FQDN of the server to be controlled with Ansible. E.g.: `idp.dir.garr.it.yml`
* `example/example.ini`:

  template file containing all the hosts on which Ansible is to act.

  Copy this file to a new file whose name contains the name of the environment that Ansible needs to check. E.g.: `development.ini`
* `files/all/`:

  folder containing utility files for all servers controlled by Ansible.

* `files/idp.example.org/`:

  template folder containing the files used by the server configured with Ansible.

  Copy this folder to a new folder whose name contains the FQDN of the server to be configured. E.g.: `idp.dir.garr.it/`.

  Within it are:

  * `ssh/authorized_keys`:

    contains the SSH keys used to access the server via SSH through the user "**debian**".

  * `shibboleth-idp/`:
  
    contains all files and folders that will be replaced to those generated from scratch by a new installation for a Shibboleth Identity Provider.

  * `ssl/`:

    contains the files required for HTTPS/SSL protection of the server.
