#!/usr/bin/env python3

import os
import logging
import subprocess
import pexpect
from utils import yml
from string import Template

# PARAMETERS

# END PARAMETERS

def gen_shib_md_credentials(fqdn, idp_credentials_dir, rsa_bits=3072, ans_vault_file=""):

    s = Template(
        '''[req]
        default_bits=$rsa_bits
        default_md=sha256
        encrypt_key=no
        distinguished_name=dn
        # PrintableStrings only
        string_mask=MASK:0002
        prompt=no
        x509_extensions=ext
        
        [dn]
        CN=$fqdn
        
        [ext]
        subjectAltName = DNS:$fqdn
        subjectKeyIdentifier=hash'''
    )

    backchannel_p12_export_pw = yml.get_random_str(64)
    sealer_pw = yml.get_random_str(64)
    openssl_credential = s.substitute(dict(fqdn=fqdn, rsa_bits=rsa_bits))

    if (idp_credentials_dir.endswith("/")):
        idp_credentials_dir = idp_credentials_dir.rstrip(idp_credentials_dir[-1])

    if os.path.exists(f"{idp_credentials_dir}/metadata-{fqdn}-credentials.cnf"):
        logging.debug(f"Metadata Credentials for {fqdn} already created.")

        backchannel_p12_export_pw_file = open(f"{idp_credentials_dir}/backchannel_p12_{fqdn}_pw.txt", "r")
        backchannel_p12_export_pw = backchannel_p12_export_pw_file.read()
        backchannel_p12_export_pw_file.close()

        sealer_pw_file = open(f"{idp_credentials_dir}/sealer_{fqdn}_pw.txt", "r")
        sealer_pw = sealer_pw_file.read()
        sealer_pw_file.close()

        if "ANSIBLE_VAULT" in backchannel_p12_export_pw:
            backchannel_p12_export_pw = subprocess.run(
                f"ansible-vault view --vault-password-file {ans_vault_file} {idp_credentials_dir}/backchannel_p12_{fqdn}_pw.txt", shell=True, capture_output=True, text=True).stdout.strip()

        if "ANSIBLE_VAULT" in sealer_pw:
            sealer_pw = subprocess.run(
                f"ansible-vault view --vault-password-file {ans_vault_file} {idp_credentials_dir}/sealer_{fqdn}_pw.txt", shell=True, capture_output=True, text=True).stdout.strip()

        return sealer_pw,backchannel_p12_export_pw
    else:
        logging.debug(f"Creating Metadata Certificate and Key for {fqdn}...")

        if not os.path.exists(idp_credentials_dir):
           os.makedirs(idp_credentials_dir)

        f = open(f"{idp_credentials_dir}/metadata-{fqdn}-credentials.cnf", "w")
        f.write(openssl_credential)
        f.close()
        logging.debug(f"{idp_credentials_dir}/metadata-{fqdn}-credentials.cnf created.")

    if ((not os.path.exists(f"{idp_credentials_dir}/idp-backchannel.crt")) or (not os.path.exists(f"{idp_credentials_dir}/idp-backchannel.p12")) or (not os.path.exists(f"{idp_credentials_dir}/idp-backchannel.key"))):
        command = f"openssl req -new -x509 -config {idp_credentials_dir}/metadata-{fqdn}-credentials.cnf -out {idp_credentials_dir}/idp-backchannel.crt --keyout {idp_credentials_dir}/idp-backchannel.key -days 7300"
        subprocess.run(command, shell=True)

        command = f"openssl pkcs12 -export -out {idp_credentials_dir}/idp-backchannel.p12 -inkey {idp_credentials_dir}/idp-backchannel.key -in {idp_credentials_dir}/idp-backchannel.crt"
        child = pexpect.spawn('/bin/bash', ['-c', command])
        # Compatible with:
        # * Debian: 'Enter Export Password:' & 'Verifying - Enter Export Password:'
        # * Ubuntu: 'Verifying - Enter Export Password:'
        child.expect(['Enter Export Password:'])
        child.sendline(backchannel_p12_export_pw)
        child.expect(['Verifying - Enter Export Password:'])
        child.sendline(backchannel_p12_export_pw)

        logging.debug(f"{idp_credentials_dir}/idp-backchannel.crt created.")
        logging.debug(f"{idp_credentials_dir}/idp-backchannel.p12 created.")
        logging.debug(f"{idp_credentials_dir}/idp-backchannel.key created.")

    if ((not os.path.exists(f"{idp_credentials_dir}/idp-signing.crt")) or (not os.path.exists(f"{idp_credentials_dir}/idp-signing.key"))):
        command = f"openssl req -new -x509 -config {idp_credentials_dir}/metadata-{fqdn}-credentials.cnf -out {idp_credentials_dir}/idp-signing.crt --keyout {idp_credentials_dir}/idp-signing.key -days 7300"
        subprocess.run(command, shell=True)

        logging.debug(f"{idp_credentials_dir}/idp-signing.crt created.")
        logging.debug(f"{idp_credentials_dir}/idp-signing.key created.")

    if ((not os.path.exists(f"{idp_credentials_dir}/idp-encryption.crt")) or (not os.path.exists(f"{idp_credentials_dir}/idp-encryption.key"))):
        command = f"openssl req -new -x509 -config {idp_credentials_dir}/metadata-{fqdn}-credentials.cnf -out {idp_credentials_dir}/idp-encryption.crt --keyout {idp_credentials_dir}/idp-encryption.key -days 7300"
        subprocess.run(command, shell=True)

        logging.debug(f"{idp_credentials_dir}/idp-encryption.crt created.")
        logging.debug(f"{idp_credentials_dir}/idp-encryption.key created.")

    if (os.path.isfile(ans_vault_file)):
        # Encrypt KEY with Ansible Vault
        subprocess.run(
            f"ansible-vault encrypt {idp_credentials_dir}/idp-backchannel.p12 --vault-password-file {ans_vault_file}", shell=True)
        subprocess.run(
            f"ansible-vault encrypt {idp_credentials_dir}/idp-backchannel.key --vault-password-file {ans_vault_file}", shell=True)
        subprocess.run(
            f"ansible-vault encrypt {idp_credentials_dir}/idp-signing.key --vault-password-file {ans_vault_file}", shell=True)
        subprocess.run(
            f"ansible-vault encrypt {idp_credentials_dir}/idp-encryption.key --vault-password-file {ans_vault_file}", shell=True)

        logging.debug(f"IdP Metadata Credentials created and Ansible Vaulted into {idp_credentials_dir}")

        # Generate a file containing the Credentials Password
        backchannel_p12_export_pw_file = open(f"{idp_credentials_dir}/backchannel_p12_{fqdn}_pw.txt", "w")
        backchannel_p12_export_pw_file.write(backchannel_p12_export_pw)
        backchannel_p12_export_pw_file.close()

        subprocess.run(
            f"ansible-vault encrypt {idp_credentials_dir}/backchannel_p12_{fqdn}_pw.txt --vault-password-file {ans_vault_file}", shell=True)

        # Generate a file containing the Credentials Password
        sealer_pw_file = open(f"{idp_credentials_dir}/sealer_{fqdn}_pw.txt", "w")
        sealer_pw_file.write(sealer_pw)
        sealer_pw_file.close()

        subprocess.run(
            f"ansible-vault encrypt {idp_credentials_dir}/sealer_{fqdn}_pw.txt --vault-password-file {ans_vault_file}", shell=True)

        return sealer_pw,backchannel_p12_export_pw

    else:
        backchannel_p12_export_pw_file = open(f"{idp_credentials_dir}/backchannel_p12_{fqdn}_pw.txt", "w")
        backchannel_p12_export_pw_file.write(backchannel_p12_export_pw)
        backchannel_p12_export_pw_file.close()

        sealer_pw_file = open(f"{idp_credentials_dir}/sealer_{fqdn}_pw.txt", "w")
        sealer_pw_file.write(sealer_pw)
        sealer_pw_file.close()

        logging.debug(f"IdP Metadata Credentials created into {idp_credentials_dir}")

        return sealer_pw,backchannel_p12_export_pw

'''
def gen_sealer_keystore_pw(fqdn, idp_entity_id, idp_credentials_dir, ans_vault_file="", rsa_bits=3072):

    # Create a password long 64 characters
    #result = subprocess.run("openssl rand -base64 48", capture_output=True, shell=True, text=True)
    #idp_cred_pw = result.stdout.strip()
    p12_export_pw = yml.get_random_str(64)

    logging.debug(f"IdP Credentials password: {p12_export_pw}")

    # Create IDP Credentials DIR
    if not os.path.exists(idp_credentials_dir):
       os.makedirs(idp_credentials_dir)

    logging.debug(f"IdP 'credentials' directory created in {idp_credentials_dir}")

    # Sealer JKS and KVER have to be created directly on the Shibboleth IdP

    # Generate all Shibboleth IdP credentials (backchannel, signing, ecryption) if they are not exists already
    gen_shib_md_credentials(fqdn, idp_credentials_dir, p12_export_pw, rsa_bits, ans_vault_file)

    # Generate a file containing the Credentials Password
    p12_export_pw_file = open(f"{idp_credentials_dir}/{fqdn}_pw.txt", "w")
    p12_export_pw_file.write(p12_export_pw)
    p12_export_pw_file.close()

    # Ansible Vault the Credentials Password to be able to save it on GIT
    if (os.path.isfile(ans_vault_file)):
        subprocess.run(
            f"ansible-vault encrypt {idp_credentials_dir}/{fqdn}_pw.txt --vault-password-file {ans_vault_file}", shell=True)
        return p12_export_pw

    else:
        p12_export_pw_file = open(f"{idp_credentials_dir}/{fqdn}_pw.txt", "r")
        p12_export_pw = p12_export_pw_file.read()
        p12_export_pw_file.close()
        if "ANSIBLE_VAULT" in p12_export_pw:
            p12_export_pw = subprocess.run(
                f"ansible-vault view --vault-password-file {ans_vault_file} {idp_credentials_dir}/{fqdn}_pw.txt").stdout.strip()
            return p12_export_pw

        return p12_export_pw
'''
