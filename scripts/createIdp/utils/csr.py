#!/usr/bin/env python3

'''The methods provided here are neeed to create CSR and/or Private Key for an SSL certificate'''

# Libraries/Modules
import os
import logging
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.backends import default_backend

# Generate Certificate Signing Request (CSR)
def generate_csr(fqdn, dest, key_size=3072, req_info='No', sans=[]):
    if not os.path.exists(f"{dest}/{fqdn}.key"):

        if not os.path.exists(dest):
            os.makedirs(dest)

        csr_file_path = f"{dest}/{fqdn}.csr"
        private_key_file_path = f"{dest}/{fqdn}.key"
        keysize = key_size

        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=keysize,
            backend=default_backend()
        )
    
        subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "IT"),
            x509.NameAttribute(NameOID.COMMON_NAME, fqdn)
        ])
    
        csr = x509.CertificateSigningRequestBuilder().subject_name(
            subject
        ).sign(private_key, hashes.SHA256(), default_backend())
    
        csr_pem = csr.public_bytes(
            encoding=serialization.Encoding.PEM
        )
    
        with open(private_key_file_path, "wb") as private_key_file:
            private_key_file.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                )
            )
    
        with open(csr_file_path, "wb") as csr_file:
            csr_file.write(csr_pem)

        return 1

    else:
        logging.debug(f"CSR and KEY for {fqdn} are already created in: {dest}")
        return 0

