#!/usr/bin/env python3

'''
lang_dict = {
    'en': 'English',
    'it': 'Italian',
    'fr': 'French',
    'de': 'German',
    'es': 'Spanish',
    'zh': 'Chinese',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'pt': 'Portuguese',
    'ja': 'Japanese'
}
'''
from collections import OrderedDict

def get_yml_questions(lang_dict = {'en': 'English'}):

    questions_dict = OrderedDict()

    #for lang in lang_dict.keys():
    #    questions_dict[f"mdui_displayName_{lang}"] = f"Insert the Institution Name for the '{lang_dict[lang]}' language: "
    #    questions_dict[f"mdui_description_{lang}"] = f"Insert Institution IdP description for the '{lang_dict[lang]}' language (press Enter to keep the default value): "
    #    questions_dict[f"org_url_{lang}"] = f"Insert the Institution site for the '{lang_dict[lang]}' language: "
    #    questions_dict[f"mdui_privacy_{lang}"] = f"Insert the URL of the Privacy Policy page valid for the Institution in '{lang_dict[lang]}' language (press Enter to keep the default value): "
    #    questions_dict[f"mdui_info_{lang}"] = f"Insert the URL of the Information page valid for the Institution in '{lang_dict[lang]}' language (press Enter to keep the default value): "
    
    questions_dict["idp_scope"] = "Insert the Shibboleth IdP scopes separated by a comma: "
    questions_dict["idp_displayname"] = "Insert the Name of your Institution: "
    questions_dict["idp_technical_email"] = "Insert the Technical Contact e-mail address for the Institutional IdP (press Enter to leave it empty): "
    questions_dict["org_url"] = "Insert the Institution site for the English language: "
    questions_dict["ca"] = "Insert the URL where the Certification Authority PEM certificate (press 'Enter' for ACME or insert 'GEANT' for 'GEANT_OV_RSA_CA_4'): "
    questions_dict["idp_persistentId_salt"] = "Insert the persistent-id salt (press Enter to generate a random value): "
    questions_dict["idp_authn_LDAP_ldapURL"] = "Insert the LDAP URL (e.g.: ldap://idm.example.org)"
    questions_dict["idp_authn_LDAP_bindDN"] = "Insert the LDAP bindDN of the user who can found the others (e.g.: cn=idm-user,ou=system,dc=example,dc=org)"
    questions_dict["idp_authn_LDAP_baseDN"] = "Insert the LDAP baseDN where users are stored (e.g.: ou=people,dc=example,dc=org): "
    questions_dict["idp_authn_LDAP_bindDNCredential"] = "Insert the 'idpuser' user password (press Enter to generate a random value): "
    questions_dict["root_user_pw"] = "Insert the 'root' user password (press Enter to generate a random value): "

    return questions_dict
