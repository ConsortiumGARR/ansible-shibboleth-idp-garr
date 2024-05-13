#!/usr/bin/env python3

import argparse
import os
import shutil
import logging
from utils import csr,idp,ini,yml

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("fqdn",
                        help="Full Qualified Domain Name of Shibboleth IdP")
    parser.add_argument("environment",
                        help="Full name of the environment (production, development, staging, test)")
    parser.add_argument("--entityid",
                        help="Provide the entityID for the IdP", action="store", default="")
    parser.add_argument("--force",
                        help="Force regeneration ansible-shibboleth-idp-garr YML file", action="store_true", default=False)
    parser.add_argument("--csr",
                        help="Generate SSL CSR and SSL Key Only", action="store_true", default=False)
    parser.add_argument("--yml",
                        help="Generate IdP YML file Only", action="store_true", default=False)
    parser.add_argument("--everything",
                        help="Generate SSL credentials and IdP YML files", action="store_true", default=True)
    args = parser.parse_args()

    # CONSTANTS STARTS
    ANS_SHIB = f"{os.path.dirname(os.path.realpath(__file__))}"
    ANS_VAULT_FILE = f"{ANS_SHIB}/.vault_pass"
    ANS_SHIB_INV = f"{ANS_SHIB}/inventories"
    ANS_SHIB_FILES_DIR = f"{ANS_SHIB_INV}/files"
    ANS_SHIB_INV_ENV = f"{ANS_SHIB_INV}/{args.environment}"

    IDP_ENV_HOST_VARS = f"{ANS_SHIB_INV_ENV}/host_vars"
    IDP_YML = f"{IDP_ENV_HOST_VARS}/{args.fqdn}.yml"

    IDP_FILES_DIR = f"{ANS_SHIB_FILES_DIR}/{args.fqdn}"
    IDP_SAMPLE_FILES_DIR = f"{ANS_SHIB_FILES_DIR}/sample-FQDN-dir"
    IDP_PLA_FILES_DIR = f"{IDP_FILES_DIR}/phpldapadmin"
    IDP_SSL_DIR = f"{IDP_FILES_DIR}/ssl"
    IDP_CRED_DIR = f"{IDP_FILES_DIR}/shibboleth-idp/credentials"
    IDP_STYLES_DIR = f"{IDP_FILES_DIR}/idp-styles"

    RSA_BITS = 3072
    
    LANG_DICT = {
        'en': 'English',
        'it': 'Italian'
    }
    # CONSTANTS END

    # Remove LOG file before start
    os.system("cat /dev/null > logs/createIdP.log")

    # Create a new LOG file
    logging.basicConfig(filename='logs/createIdP.log', format='%(asctime)s - %(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S', level=logging.DEBUG)

    # If I need to force the creation of an already existent IdP I need to '--force' it
    if (args.force):
        logging.debug(f"Removing '{args.fqdn}' files...")
        os.system(
            f"sed -i '/{args.fqdn}/d' {ANS_SHIB_INV_ENV}/{args.environment}.ini")

        if (os.path.isfile(IDP_YML)):
            os.remove(IDP_YML)

        shutil.rmtree(IDP_FILES_DIR)
        logging.debug("...files deleted.")

    # If I run the script with the "--csr" parameter
    if (args.csr):
        logging.debug(f"Creating SSL CSR and KEY for '{args.fqdn}' ...")
        # Create CSR and KEY for the IdP, if not exist, in IDP_SSL_DIR
        csr.generate_csr(args.fqdn, IDP_SSL_DIR, RSA_BITS)
        logging.debug("...SSL CSR and KEY created.")

    # If I run the script with "--yml" parameter
    if (args.yml):
        logging.debug(f"Creating IdP credentials for '{args.fqdn}' ...")
        idp_sealer_pw,backchannel_p12_export_pw = idp.gen_shib_md_credentials( args.fqdn, 
                                                                               IDP_CRED_DIR,
                                                                               RSA_BITS,
                                                                               ANS_VAULT_FILE
                                                                             )
        logging.debug("...IdP credentials created.")

        # Create the IdP YAML file and ecrypt it with Ansible Vault, if Ansible Vault exists
        logging.debug(f"Creating IDP YAML file for '{args.fqdn}' ...")
        yml.create_idp_yml(
            args.fqdn,
            args.entityid,
            IDP_SSL_DIR,
            IDP_YML,
            IDP_STYLES_DIR,
            IDP_PLA_FILES_DIR,
            ANS_SHIB_FILES_DIR,
            idp_sealer_pw,
            backchannel_p12_export_pw,
            LANG_DICT,
            ANS_VAULT_FILE
        )
        logging.debug("...IDP YAML file created.")

    # If I run script with "fqdn", "environment" and "--everything" parameter I will follow all steps
    if (args.everything):
        logging.debug(f"Creating all needed files for '{args.fqdn}' IdP ...")
        logging.debug("Creating SSL CSR and KEY ...")

        # Create CSR and KEY for the IdP, if not exist, in the IDP_SSL_DEST directory
        csr.generate_csr(args.fqdn, IDP_SSL_DIR)
        logging.debug("...SSL CSR and KEY created.")

        logging.debug("Creating IdP credentials ...")
        # Create or Retrieve the Shibboleth IdP sealer/keystore password
        idp_sealer_pw,backchannel_p12_export_pw = idp.gen_shib_md_credentials( args.fqdn,
                                                                               IDP_CRED_DIR,
                                                                               RSA_BITS,
                                                                               ANS_VAULT_FILE,
                                                                             )
        logging.debug("...IdP credentials created.")

        logging.debug("Creating IDP YAML file ...")
        # Create the IdP YAML file
        idp_type = yml.create_idp_yml( args.fqdn,
                                       args.entityid,
                                       IDP_SSL_DIR,
                                       IDP_YML,
                                       IDP_STYLES_DIR,
                                       IDP_PLA_FILES_DIR,
                                       ANS_SHIB_FILES_DIR,
                                       idp_sealer_pw,
                                       backchannel_p12_export_pw,
                                       LANG_DICT,
                                       ANS_VAULT_FILE,
                                     )
        logging.debug("...IDP YAML file created.")

        # Add the new IdP on the production.ini file
        logging.debug(f"Adding the IDP to '{args.environment}' inventory...")
        ini.add_idp_to_inventory( args.fqdn,
                                  idp_type,
                                  f"{ANS_SHIB_INV_ENV}/{args.environment}.ini"
                                )
        logging.debug(f"...IDP added to '{args.environment}' inventory.")

        # Copy italian and english flags on the IdP styles dir
        #logging.debug("Copying samples flags into the IdP directory...")
        #os.system(f"cp -nr {IDP_SAMPLE_FILES_DIR}/idp/styles/it/itFlag.png {IDP_STYLES_DIR}/it/itFlag.png")
        #os.system(f"cp -nr {IDP_SAMPLE_FILES_DIR}/idp/styles/en/enFlag.png {IDP_STYLES_DIR}/en/enFlag.png")
        #logging.debug("...samples flags copied.")

        # Copy federation and interfederation logo on the IdP styles dir
        #logging.debug("Copying federation and interfederation logos into the IdP directory...")
        #os.system(f"cp -nr {IDP_SAMPLE_FILES_DIR}/idp/styles/images {IDP_STYLES_DIR}")
        #logging.debug("...federation and interfederation logos copied.")

        # Create 'idp/mysql-restore' dir with its README.md file
        #logging.debug("Copying MySQL restore directory into the IDP directory...")
        #os.system(f"cp -nr {IDP_SAMPLE_FILES_DIR}/idp/mysql-restore {IDP_FILES_DIR}/idp")
        #logging.debug("...MySQL restore directory copied.")

        # Create 'idp/conf' dir with its content
        #logging.debug("Copying IdP 'conf' directory into the IDP directory...")
        #os.system(f"cp -nr {IDP_SAMPLE_FILES_DIR}/idp/conf {IDP_FILES_DIR}/idp")
        #logging.debug("...IdP 'conf' directory copied.")

        # Create 'openldap' dir with its content
        #logging.debug("Copying IdP OpenLDAP restore directory into the IDP directory...")
        #os.system(f"cp -nr {IDP_SAMPLE_FILES_DIR}/openldap {IDP_FILES_DIR}")
        #logging.debug("...IdP OpenLDAP restore directory copied.")

    else:
        parser.print_help()
