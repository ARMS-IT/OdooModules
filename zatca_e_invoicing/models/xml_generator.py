import dicttoxml

CAC_TAGS = ['AdditionalDocumentReference','Attachment','Attachment','AccountingSupplierParty','Party','PostalAddress','Country','PartyTaxScheme','TaxScheme','PartyLegalEntity','AccountingCustomerParty','Party','PostalAddress','Country','PartyTaxScheme','TaxScheme','PartyLegalEntity','Delivery','PaymentMeans','TaxTotal','TaxSubtotal','TaxCategory','TaxScheme','LegalMonetaryTotal','TaxTotal','Item','ClassifiedTaxCategory','TaxScheme','Price','InvoiceLine']
CBC_TAGS = ['InvoiceTypeCode', 'IssueTime', 'PlotIdentification', 'PostalZone', 'CompanyID', 'StreetName', 'TaxCurrencyCode', 'CountrySubentity', 'UUID', 'ProfileID', 'TaxExclusiveAmount', 'DocumentCurrencyCode', 'Percent', 'IssueDate', 'TaxableAmount', 'PayableAmount', 'BuildingNumber', 'CitySubdivisionName', 'TaxAmount', 'EmbeddedDocumentBinaryObject', 'LatestDeliveryDate', 'TaxInclusiveAmount', 'RoundingAmount', 'ActualDeliveryDate', 'CityName', 'InvoicedQuantity', 'PaymentMeansCode', 'LineExtensionAmount', 'RegistrationName', 'TaxSubtotalTaxAmount', 'Name', 'ID', 'PriceAmount', 'AllowanceTotalAmount', 'IdentificationCode']

def generate_einvoice_xml(json_obj):
    xml_data = dicttoxml.dicttoxml(json_obj, attr_type=False)
    clean_xml_data = xml_data.decode('utf-8').replace('<root>','<Invoice xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2" xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2">').replace('</root>','</Invoice>').replace('<item>', '').replace('</item>', '')
    return update_tags(clean_xml_data)

def update_tags(xml_string):
    for tag in CAC_TAGS:
        xml_string = xml_string.replace("<{}>".format(tag), "<cac:{}>".format(tag)).replace('</{}>'.format(tag), "</cac:{}>".format(tag))

    for tag in CBC_TAGS:
        xml_string = xml_string.replace("<{}>".format(tag), "<cbc:{}>".format(tag)).replace('</{}>'.format(tag), "</cbc:{}>".format(tag))

    return xml_string

