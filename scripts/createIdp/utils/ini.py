#!/usr/bin/env python3

from configparser import ConfigParser

### Function needed to manage Inventory files ###

def add_idp_to_inventory(idp_fqdn, idp_type, inventory_ini_file):
   
   config = ConfigParser(allow_no_value=True,delimiters=(' '))
   config.read(inventory_ini_file)
   if idp_type not in config:
      config.add_section(idp_type)
   config.set(idp_type, idp_fqdn, f"ansible_host={idp_fqdn} ansible_connection=ssh ansible_user=debian ansible_ssh_private_key_file=/home/mala/garrbox/Apps/Asbru-SSH/personal/id_rsa_new")

   inv_file = open(inventory_ini_file,"w")
   config.write(inv_file,space_around_delimiters=False)

def del_idp_to_inventory(idp_fqdn, idp_type, inventory_ini_file):
   
   config = ConfigParser(allow_no_value=True)
   config.read(inventory_ini_file)
   config.remove_option(idp_type, idp_fqdn)
   #config.remove_option(idp_type, idp_fqdn, f"ansible_host={idp_fqdn} ansible_connection=ssh ansible_user=debian ansible_ssh_private_key_file=/home/mala/garrbox/Apps/Asbru-SSH/personal/id_rsa_new")

   inv_file = open(inventory_ini_file,"w")
   config.write(inv_file,space_around_delimiters=False)
