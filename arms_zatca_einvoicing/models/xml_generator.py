import dicttoxml

CAC_TAGS = ['AdditionalDocumentReference-1', 'BillingReference', 'InvoiceDocumentReference' ,'PartyIdentification-SAG', 'PartyIdentification-MLS', 'AdditionalDocumentReference-2', 'AdditionalDocumentReference-3','Attachment','Attachment','AccountingSupplierParty','Party','PostalAddress','Country','PartyTaxScheme','TaxScheme','PartyLegalEntity','AccountingCustomerParty','Party','PostalAddress','Country','PartyTaxScheme','TaxScheme','PartyLegalEntity','Delivery','PaymentMeans','TaxTotal','TaxSubtotal','TaxCategory','TaxScheme','LegalMonetaryTotal','TaxTotal-1','Item','ClassifiedTaxCategory','TaxScheme','Price','InvoiceLine', "Signature"]
CBC_TAGS = ['InvoiceTypeCode', 'LineCountNumeric', 'IssueTime', 'InstructionNote', 'PlotIdentification', 'PostalZone', 'CompanyID', 'StreetName', 'TaxCurrencyCode', 'CountrySubentity', 'UUID', 'ProfileID', 'TaxExclusiveAmount', 'DocumentCurrencyCode', 'Percent', 'IssueDate', 'TaxableAmount', 'PayableAmount', 'BuildingNumber', 'CitySubdivisionName', 'TaxAmount', 'EmbeddedDocumentBinaryObject', 'LatestDeliveryDate', 'TaxInclusiveAmount', 'RoundingAmount', 'ActualDeliveryDate', 'CityName', 'InvoicedQuantity', 'PaymentMeansCode', 'LineExtensionAmount', 'RegistrationName', 'Name', 'ID', 'PriceAmount', 'AllowanceTotalAmount', 'IdentificationCode', "SignatureMethod"]
EXT_TAGS = ['UBLExtensions', 'UBLExtension', 'ExtensionURI', 'ExtensionContent', ]
SAC_TAGS = ['SignatureInformation', '']
SBC_TAGS = ['ReferencedSignatureID', '']
SIG_TAGS = ['UBLDocumentSignatures', ]
DS_TAGS = ["ds_Signature", "SignedInfo", "DigestMethod", "X509IssuerName", "X509SerialNumber", "DigestValue", "CanonicalizationMethod", "SignatureValue", "KeyInfo", "X509Data", "X509Certificate", "ds_SignatureMethod", "Reference", "Reference1", "Reference2", "Transforms", "Transform", "Transform1", "Transform2", "Transform3", "Transform4", "XPath", "Object"]
XADES_TAGS = ["QualifyingProperties", "SignedProperties", "SignedSignatureProperties", "SigningTime", "SigningCertificate", "Cert", "CertDigest", "IssuerSerial", ]

def generate_einvoice_xml(json_obj, invoice_lines_count):
    xml_data = dicttoxml.dicttoxml(json_obj, attr_type=False)
    clean_xml_data = xml_data.decode('utf-8').replace('<root>','<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2">').replace('</root>','</Invoice>').replace('<item>', '').replace('</item>', '')
    return update_tags(clean_xml_data, invoice_lines_count)

def update_tags(xml_string, invoice_lines_count):
    for tag in CAC_TAGS:
        if tag.startswith('AdditionalDocumentReference'):
            new_tag = "AdditionalDocumentReference"
            xml_string = xml_string.replace("<{}>".format(tag), "<cac:{}>".format(new_tag)).replace('</{}>'.format(tag), "</cac:{}>".format(new_tag))
        
        if tag == "PartyIdentification-MLS":
            new_tag = "PartyIdentification"
            xml_string = xml_string.replace("<{}>".format(tag), "<cac:{}><cbc:ID schemeID='MLS'>".format(new_tag)).replace('</{}>'.format(tag), "</cbc:ID></cac:{}>".format(new_tag))

        if tag == "PartyIdentification-SAG":
            new_tag = "PartyIdentification"
            xml_string = xml_string.replace("<{}>".format(tag), "<cac:{}><cbc:ID schemeID='SAG'>".format(new_tag)).replace('</{}>'.format(tag), "</cbc:ID></cac:{}>".format(new_tag))

        if tag == 'TaxTotal-1':
            new_tag = "TaxTotal"
            xml_string = xml_string.replace("<{}>".format(tag), "<cac:{}>".format(new_tag)).replace('</{}>'.format(tag), "</cac:{}>".format(new_tag))

        if tag.startswith("InvoiceLine"):
            orginal_tag = tag
            new_tag = "InvoiceLine"
            for x in range(1, invoice_lines_count+1):
                tag = "{}-{}".format(orginal_tag, x)
                xml_string = xml_string.replace("<{}>".format(tag), "<cac:{}>".format(new_tag)).replace('</{}>'.format(tag), "</cac:{}>".format(new_tag))

        else:
            xml_string = xml_string.replace("<{}>".format(tag), "<cac:{}>".format(tag)).replace('</{}>'.format(tag), "</cac:{}>".format(tag))

    for tag in CBC_TAGS:
        if tag == 'EmbeddedDocumentBinaryObject':
            xml_string = xml_string.replace("<{}>".format(tag), "<cbc:{} mimeCode='text/plain'>".format(tag)).replace('</{}>'.format(tag), "</cbc:{}>".format(tag))

        if tag == "InvoiceTypeCode":
            xml_string = xml_string.replace("<{}>".format(tag), "<cbc:{} name='0100000'>".format(tag)).replace('</{}>'.format(tag), "</cbc:{}>".format(tag))

        if tag in ["TaxAmount", "LineExtensionAmount", "TaxExclusiveAmount", "TaxInclusiveAmount", "AllowanceTotalAmount", "PayableAmount", "RoundingAmount", "PriceAmount", "TaxableAmount", "TaxAmount"]:
            xml_string = xml_string.replace("<{}>".format(tag), "<cbc:{} currencyID='SAR'>".format(tag)).replace('</{}>'.format(tag), "</cbc:{}>".format(tag))

        if tag == "InvoicedQuantity":
            xml_string = xml_string.replace("<{}>".format(tag), "<cbc:{} unitCode='PCE'>".format(tag)).replace('</{}>'.format(tag), "</cbc:{}>".format(tag))

        else:
            xml_string = xml_string.replace("<{}>".format(tag), "<cbc:{}>".format(tag)).replace('</{}>'.format(tag), "</cbc:{}>".format(tag))

    for tag in EXT_TAGS:
        xml_string = xml_string.replace("<{}>".format(tag), "<ext:{}>".format(tag)).replace('</{}>'.format(tag), "</ext:{}>".format(tag))

    for tag in SBC_TAGS:
        xml_string = xml_string.replace("<{}>".format(tag), "<sbc:{}>".format(tag)).replace('</{}>'.format(tag), "</sbc:{}>".format(tag))

    for tag in SAC_TAGS:
        xml_string = xml_string.replace("<{}>".format(tag), "<sac:{}>".format(tag)).replace('</{}>'.format(tag), "</sac:{}>".format(tag))

    for tag in SIG_TAGS:
        if tag == 'UBLDocumentSignatures':
            xml_string = xml_string.replace("<{}>".format(tag), "<sig:{} xmlns:sig='urn:oasis:names:specification:ubl:schema:xsd:CommonSignatureComponents-2' xmlns:sac='urn:oasis:names:specification:ubl:schema:xsd:SignatureAggregateComponents-2' xmlns:sbc='urn:oasis:names:specification:ubl:schema:xsd:SignatureBasicComponents-2'>".format(tag)).replace('</{}>'.format(tag), "</sig:{}>".format(tag))
        else:
            xml_string = xml_string.replace("<{}>".format(tag), "<sig:{}>".format(tag)).replace('</{}>'.format(tag), "</sig:{}>".format(tag))

    for tag in DS_TAGS:
        if tag == 'ds_Signature':
            new_tag = 'Signature'
            xml_string = xml_string.replace("<{}>".format(tag), "<ds:{} xmlns:ds='http://www.w3.org/2000/09/xmldsig#' Id='signature'>".format(new_tag)).replace('</{}>'.format(tag), "</ds:{}>".format(new_tag))
        
        if tag == "CanonicalizationMethod":
            xml_string = xml_string.replace("<{}>".format(tag), "<ds:{} Algorithm='http://www.w3.org/2006/12/xml-c14n11'>".format(tag)).replace('</{}>'.format(tag), "</ds:{}>".format(tag))

        if tag == "ds_SignatureMethod":
            new_tag = "SignatureMethod"
            xml_string = xml_string.replace("<{}>".format(tag), "<ds:{} Algorithm='http://www.w3.org/2001/04/xmldsig-more#rsa-sha256'>".format(new_tag)).replace('</{}>'.format(tag), "</ds:{}>".format(new_tag))

        if tag == "Transform":
            xml_string = xml_string.replace("<{}>".format(tag), "<ds:{} Algorithm='http://www.w3.org/2006/12/xml-c14n11'>".format(tag)).replace('</{}>'.format(tag), "</ds:{}>".format(tag))

        if tag.startswith("Transform") and tag != "Transforms" and tag != "Transform":
            new_tag = "Transform"
            xml_string = xml_string.replace("<{}>".format(tag), "<ds:{} Algorithm='http://www.w3.org/TR/1999/REC-xpath-19991116'>".format(new_tag)).replace('</{}>'.format(tag), "</ds:{}>".format(new_tag))

        if tag.startswith("Reference") and tag != "ReferencedSignatureID":
            new_tag = "Reference"
            if tag == "Reference1":
                xml_string = xml_string.replace("<{}>".format(tag), "<ds:{} Id='invoiceSignedData' URI=''>".format(new_tag)).replace('</{}>'.format(tag), "</ds:{}>".format(new_tag))
                    
            if tag == "Reference2":
                xml_string = xml_string.replace("<{}>".format(tag), "<ds:{} Type='http://www.w3.org/2000/09/xmldsig#SignatureProperties' URI='#xadesSignedProperties'>".format(new_tag)).replace('</{}>'.format(tag), "</ds:{}>".format(new_tag))

        if tag == "DigestMethod":
            xml_string = xml_string.replace("<{}>".format(tag), "<ds:{} Algorithm='http://www.w3.org/2001/04/xmlenc#sha256'>".format(new_tag)).replace('</{}>'.format(tag), "</ds:{}>".format(new_tag))

        else:
            xml_string = xml_string.replace("<{}>".format(tag), "<ds:{}>".format(tag)).replace('</{}>'.format(tag), "</ds:{}>".format(tag))
    
    for tag in XADES_TAGS:
        if tag == "SignedProperties":
            xml_string = xml_string.replace("<{}>".format(tag), "<xades:{} Id='xadesSignedProperties'>".format(tag)).replace('</{}>'.format(tag), "</xades:{}>".format(tag))

        if tag == "QualifyingProperties":
            xml_string = xml_string.replace("<{}>".format(tag), "<xades:{} xmlns:xades='http://uri.etsi.org/01903/v1.3.2#' Target='signature'>".format(tag)).replace('</{}>'.format(tag), "</xades:{}>".format(tag))

        else:
            xml_string = xml_string.replace("<{}>".format(tag), "<xades:{}>".format(tag)).replace('</{}>'.format(tag), "</xades:{}>".format(tag))
    
            
    return xml_string
