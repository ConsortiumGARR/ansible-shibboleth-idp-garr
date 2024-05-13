#!/usr/bin/env python3

import os
import random
import sys
import requests
import subprocess
import uuid
import hashlib
import utils
# pip install validators
import validators
import logging

from string import Template

### FUNCTIONS NEEDED TO CREATE IDP YAML FILE ###


def get_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)


def get_random_str(string_length):
    """Returns a random string of length string_length."""
    random = hashlib.sha256(str(uuid.uuid4()).encode('utf-8')).hexdigest()  # Generate SHA256.
    return random[0:string_length]  # Return the random string.


def get_basedn_from_domain(domain):
    return "dc="+domain.replace(".", ",dc=")


def create_idp_yml(idp_fqdn, idp_entityID, ca_dest, yml_dest, idp_styles_dir, idp_pla_files_dir, files_dir, idp_sealer_keystore_pw, backchannel_p12_export_pw, lang_dict, ans_vault_file):

    if (os.path.isfile(yml_dest)):
        logging.debug(f"IdP YAML file already exist at: {yml_dest}")
    else:
        # https://www.w3.org/International/questions/qa-choosing-language-tags:
        #   lang_list contains the value of 'Subtag' of languages found on https://www.iana.org/assignments/language-subtag-registry/language-subtag-registry
        questions_dict = utils.lang.get_yml_questions(lang_dict)

        vals = {}

        vals['fqdn'] = idp_fqdn
        vals['idp_type'] = 'shib_idp'
        vals['sealer_keystore_password'] = idp_sealer_keystore_pw
        vals['backchannel_p12_export_pw'] = backchannel_p12_export_pw

        if (idp_entityID):
            vals['entityID'] = idp_entityID
        else:
            vals['entityID'] = f"https://{idp_fqdn}/idp/shibboleth"

        for key, question in questions_dict.items():

            result = ""
            logging.debug(f"Question: {question}")
            logging.debug(f"Key: {key}")

            while (result == "" or result is None):
                result = input(question)

                if (key == "ca"):
                    
                    if (result == "" or result is None):
                        logging.debug("ACME selected.")
                        vals['ca_type'] = "ACME"
                        vals[key] = f"/etc/letsencrypt/live/{idp_fqdn}/chain.pem"
                        vals['acme_email'] = input('ACME Email: ')
                        vals['acme_url'] = input('ACME URL: ')
                        vals['acme_key_id'] = input('ACME_KEY_ID: ')
                        vals['acme_hmac'] = input('ACME_HMAC_KEY: ')
                        vals['rsa_key_size'] = input('RSA KEY SIZE: ')
                    elif (result == "GEANT"):
                        logging.debug("Traditional GEANT CA selected.")
                        vals['ca_type'] = "GEANT"
                        vals[key] = "GEANT_OV_RSA_CA_4.pem"
                        
                        response_geant = requests.get("https://crt.sh/?d=2475254782")
                        with open(f"{ca_dest}/GEANT_OV_RSA_CA_4.pem", "wb") as geant_file:
                            geant_file.write(response_geant.content)

                        response_sectigo = requests.get("https://crt.sh/?d=924467857")
                        with open("/tmp/SectigoRSAOrganizationValidationSecureServerCA.crt", "wb") as sectigo_file:
                            sectigo_file.write(response_sectigo.content)

                        with open("/tmp/SectigoRSAOrganizationValidationSecureServerCA.crt", "rb") as sectigo_file:
                            sectigo_cert_content = sectigo_file.read()

                        with open(f"{ca_dest}/GEANT_OV_RSA_CA_4.pem", "ab") as geant_file:
                            geant_file.write(sectigo_cert_content)
                        
                        if os.path.exists("/tmp/SectigoRSAOrganizationValidationSecureServerCA.crt"):
                            os.remove("/tmp/SectigoRSAOrganizationValidationSecureServerCA.crt")
                    else:
                        logging.debug("Other CA selected.")
                        vals['ca_type'] = "other_ca"

                        check_url = validators.url(result)
                        while (check_url is True):
                            result = input(question)
                            check_url = validators.url(result)

                        r = requests.get(result)
                        filenameCA = result.rsplit('/', 1)[-1]
                        with open(f"{ca_dest}/{filenameCA}", 'wb') as f:
                            f.write(r.content)
                        vals[key] = filenameCA

                if (key.startswith('org_url_')):
                    check_url = validators.url(result)
                    while (check_url is not True):
                        result = input(question)
                        check_url = validators.url(result)

                # MDUI
                if (key.startswith("mdui_description_") and (result == "" or result is None)):
                    result = f"{vals['mdui_displayName_en']} Identity provider"

                # Default MDUI Info and Privacy web pages of the IDP
                # are created upon these templates:
                #
                # 1) /opt/ansible-shibboleth-idp-garr/roles/idp/templates/styles/en/info.html.j2
                # 2) /opt/ansible-shibboleth-idp-garr/roles/idp/templates/styles/it/info.html.j2
                # 3) /opt/ansible-shibboleth-idp-garr/roles/idp/templates/styles/en/privacy.html.j2
                # 4) /opt/ansible-shibboleth-idp-garr/roles/idp/templates/styles/it/privacy.html.j2

#                for lang in lang_dict.keys():
                if (key.startswith("mdui_privacy_")):
                    lang = key.split("_")[2]

                    if (result == "" or result is None):
                        result = f"https://{idp_fqdn}/{lang}/privacy.html"
                    else:
                        check_url = validators.url(result)
                        while (check_url is not True):
                            result = input(question)

                            if (result == "" or result is None):
                                result = f"https://{idp_fqdn}/{lang}/privacy.html"
                                check_url = True
                            elif (validators.url(result)):
                                check_url = True

                if (key.startswith("mdui_info_")):
                    lang = key.split("_")[2]

                    if (result == "" or result is None):
                        result = f"https://{idp_fqdn}/{lang}/info.html"
                    else:
                        check_url = validators.url(result)
                        while (check_url is not True):
                            result = input(question)

                            if (result == "" or result is None):
                                result = f"https://{idp_fqdn}/{lang}/info.html"
                                check_url = True
                            elif (validators.url(result)):
                                check_url = True

                # IdP Logo:
                # It will be stored on the IdP storage
                # and will be available on "/logo.png" location
                if (key == "mdui_logo"):
                    subprocess.run(f"mkdir -p {idp_styles_dir}", shell=True)

                    if (result == "" or result is None):
                        result = f"https://{idp_fqdn}/logo.png"
                    else:
                        check_url = validators.url(result)
                        while (check_url is not True):
                            result = input(question)

                            if (result == "" or result is None):
                                result = f"https://{idp_fqdn}/logo.png"
                            else:
                                check_url = validators.url(result)

                        if (result != f"https://{idp_fqdn}/logo.png"):
                            r = requests.get(result)
                            with open(f"{idp_styles_dir}/logo.png", 'wb') as f:
                                f.write(r.content)

                    result = f"https://{idp_fqdn}/logo.png"

                # IdP Favicon
                # It will be stored on the IdP storage
                # and will be available on "/favicon.png" location
                if (key == "mdui_favicon"):
                    subprocess.run(f"mkdir -p {idp_styles_dir}", shell=True)

                    if (result == "" or result is None):
                        result = f"https://{idp_fqdn}/favicon.png"
                    else:
                        check_url = validators.url(result)
                        while (check_url is not True):
                            result = input(question)

                            if (result == "" or result is None):
                                result = f"https://{idp_fqdn}/favicon.png"
                            else:
                                check_url = validators.url(result)

                        if (result != f"https://{idp_fqdn}/favicon.png"):
                            r = requests.get(result)
                            with open(f"{idp_styles_dir}/favicon.png", 'wb') as f:
                                f.write(r.content)

                    result = f"https://{idp_fqdn}/favicon.png"

                # IdP Support Contact
                if (key == "idp_support_email"):
                    check_email = validators.email(result)
                    while (check_email is not True):
                        if (result == "" or result is None):
                            result = "Missing"
                            check_email = True
                        else:
                            result = input(question)
                            check_email = validators.email(result)

                # IdP Technical Contact
                if (key == "idp_technical_email"):
                    check_email = validators.email(result)
                    while (check_email is not True):
                        if (result == "" or result is None):
                            result = "Missing"
                            check_email = True
                        else:
                            result = input(question)
                            check_email = validators.email(result)

                if (key == "idp_persistentId_salt" and (result == "" or result is None)):
                    result = get_random_str(64)

                if (key == "idp_fticks_salt" and (result == "" or result is None)):
                    result = get_random_str(64)

                if (key == "mariadb_root_password" and (result == "" or result is None)):
                    result = get_random_str(64)

                if (key == "idp_authn_LDAP_bindDNCredential" and (result == "" or result is None)):
                    result = get_random_str(64)

                if (key == "root_user_pw" and (result == "" or result is None)):
                    result = get_random_str(16)

            vals[key] = result

        # Create the IdP YAML file
        if (vals['ca_type'] == 'GEANT'):
            idp_yml = open(
                f"{sys.path[0]}/templates/geant-ca-idp-yml.template", 'r').read()

            yaml = open(yml_dest, "w")
            yaml.write(Template(idp_yml).safe_substitute(vals))
            yaml.close()
        elif (vals['ca_type'] == 'ACME'):
            idp_yml = open(
                f"{sys.path[0]}/templates/acme-idp-yml.template", 'r').read()

            yaml = open(yml_dest, "w")
            yaml.write(Template(idp_yml).safe_substitute(vals))
            yaml.close()
        else:
            idp_yml = open(
                f"{sys.path[0]}/templates/other-idp-yml.template", 'r').read()

            yaml = open(yml_dest, "w")
            yaml.write(Template(idp_yml).safe_substitute(vals))
            yaml.close()

        # Encrypt password with Ansible Vault (if requested)
        if (os.path.isfile(ans_vault_file)):
            subprocess.run(
                f"ansible-vault encrypt {yml_dest} --vault-password-file {ans_vault_file}", shell=True)

        return vals['idp_type']
