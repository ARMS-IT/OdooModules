CSR_CONFIG = """oid_section = OIDs
[OIDs]
certificateTemplateName = 1.3.6.1.4.1.311.20.2

[req]
default_bits = 2048
emailAddress = admin@example.com
req_extensions = v3_req
x509_extensions = v3_ca
prompt = no
default_md = sha 256
req_extensions = req_ext
distinguished_name = dn

[dn]
C=SA
OU=Riyad Branch
O=Contoso
CN=127.0.0.1

[v3_req]
basicConstraints = CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment

[req_ext]
certificateTemplateName = ASN1:PRINTABLESTRING:TSTZATCACodeSigning
subjectAltName = dirName:alt_names

[alt_names]
SN=1-TST|2-TST|3-ed22f1d8-e6a2-1118-9b58-d9a8f11e445f
UID=310122393500003
title=1100
registeredAddress= MyAddress
businessCategory=Industry"""