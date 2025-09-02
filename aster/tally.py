import frappe
import json
import requests
from frappe.utils.response import build_response
from frappe.utils import flt

Success = 200
Not_found = 400


@frappe.whitelist(allow_guest=True)
def get_sales_invoice():
    query = """
    SELECT
    si.name AS sales_invoice,
    si.customer,
    c.customer_type,
    si.address_display,
    si.shipping_address,
    si.shipping_address_name,
    si.remarks,
    si.po_no,
    si.posting_date,
    si.grand_total,
    si.rounding_adjustment,
    si_item.item_code,
    si_item.item_group,
    si_item.gst_hsn_code,
    si_item.qty,
    si_item.rate,
    si_item.description,
    si_item.warehouse,
    si_item.uom,
    si_item.item_name,
    si.grand_total AS total_amount,
    si.rounded_total,
    si.status,
    si.total_taxes_and_charges,
    si.po_no,
    si.po_date,
    si.custom_delivery_note_,
    si.custom_delivery_note_date,
    si.custom_dispatch_doc_no,
    si.custom_dispatched_through,
    si.custom_destination,
    si.custom_carrier_nameagent,
    si.custom_date,
    si.custom_bill_of_landinglrrr_no,
    si.custom_motor_vehicle_no
FROM
    `tabSales Invoice` si
INNER JOIN
    `tabSales Invoice Item` si_item ON si.name = si_item.parent
INNER JOIN
    `tabCustomer` c ON si.customer = c.name
WHERE
    si.docstatus = 1

"""

# LEFT JOIN
#     (SELECT
#         sales_invoice,
#         signed_qr_code,
#         irn,
#         creation,
#         acknowledged_on,
#         acknowledgement_number,
#         signed_invoice
#     FROM
#         `tabe-Invoice Log`) log ON si.name = log.sales_invoice
    
    
    purchase_invoices = frappe.db.sql(query, as_dict=True)

    sales_invoice_list = {}
    for invoice in purchase_invoices:
        if invoice['sales_invoice'] not in sales_invoice_list:
            print(purchase_invoices)
            buyer_address = invoice['address_display']
            # buyer_dtls = buyer_address.split("<br>")

            sales_invoice_list[invoice['sales_invoice']] = {
                "tallycode": "123456",
                "tallyname": "",
                "tallyserialno": "123456",
                "requesttype": "SALES",
                "saleslist": [{
                    'invoicenumber': invoice['sales_invoice'],
                    # 'BasicPurchaseOrderNo': invoice['po_no'],
                    # 'BasicOrderDate': invoice['po_date'],
                    'invoicedate': invoice['posting_date'].strftime('%d-%m-%Y'),
                    "narration": "",
                    'customername': invoice['customer'],
                    "parent": invoice['customer_type'],   # <-- comma added
                    "vchtype": "GST Sales",
                    "invoicemode": "Invoice Voucher View",
                    "reference": "2074/22-23",
                    "salesledger": "SGST Sales",
                    "vchclass": "Local Sales",
                    "deliverynoteno": invoice['custom_delivery_note_'],
                    "deliverynotedate": frappe.utils.formatdate(invoice['custom_delivery_note_date'], "dd-mm-yyyy"),
                    "dispatchdocno": invoice['custom_dispatch_doc_no'],
                    "dipatchthrough": invoice['custom_dispatched_through'],
                    "destination": invoice['custom_destination'],
                    "EICheckPost": invoice['custom_carrier_nameagent'],
                    "BillofLadingNo": invoice['custom_bill_of_landinglrrr_no'],
                    "BillofLadingDate": frappe.utils.formatdate(invoice['custom_date'], "dd-mm-yyyy"),
                    "lrrnumber": "",
                    "lrrdate": "",
                    "vehiclenumber": invoice['custom_motor_vehicle_no'],
                    "ordernumber": invoice['po_no'],
                    "orderdate": "27-09-2022",
                    "modeofpayment": "",
                    "otherreference": "",
                    "termsofdelivery": "",
                    "buyername": invoice['customer'],
                    "buyeraddress1": invoice['address_display'],
                    "buyeraddress2": "",
                    "buyeraddress3": "",
                    "buyeraddress4": '', # invoice['address_display'].split("<br>")[3],
                    "buyeraddress5": "",
                    "country": "",
                    "buyerstate": "",
                    "placeofsupply": "",
                    "buyergstinnumber": "", # invoice['billing_address_gstin'],
                    "deliveryname": invoice['shipping_address_name'],
                    "deliveryaddress1": invoice['shipping_address'],
                    "deliveryaddress2": "",
                    "deliveryaddress3": " ",
                    "deliveryaddress4": " ",
                    "deliveryaddress5": "",
                    "consigneestate": "",
                    "consigneegstinnumber": "", # invoice['billing_address_gstin'],
                    "subvalue": invoice['grand_total'],
                    "roundoffledger": "Rounding Off",
                    "roundoffamount": 0, # invoice['rounding_adjustment'],
                    "invoicevalue": invoice['grand_total'],
                    # invoice['rounded_total'],
                    "irn": "", # invoice['irn'],
                    "ackno": "", # invoice['acknowledgement_number'],
                    "ackdate": "", # invoice['acknowledged_on'],
                    "SignedInvoice": "", # invoice['signed_invoice'],
                    "SignedQRCode": "", # invoice['signed_qr_code'],
                    "ewaybillno": "", # invoice['ewaybill'],
                    "ewaybillnodate": "",
                    # 'grand_total': invoice['grand_total'],
                    # 'outstanding_amount': invoice['outstanding_amount'],
                    'vchproductlist': [],
                    "vchledgerlist": [
                        {
                            "invoicenumber": invoice['sales_invoice'],
                            "additionalledger": "CGST Output",
                            "parent": "",
                            "rateofpercentage": "",
                            "additionalledgervalue": round(invoice['total_taxes_and_charges']/2, 2)
                        },
                        {
                            "invoicenumber": invoice['sales_invoice'],
                            "additionalledger": "SGST Output",
                            "parent": "",
                            "rateofpercentage": "",
                            "additionalledgervalue": round(invoice['total_taxes_and_charges']/2, 2)
                        }
                    ]
                }]
            }


            query_items ="SELECT * FROM `tabSales Invoice Item` WHERE parent = %s order by idx"
                
            purchase_invoices_items= frappe.db.sql(query_items,(invoice['sales_invoice'],), as_dict=True)
            # i=0
            for item in purchase_invoices_items:
                
                item_dict = {
                    "invoicenumber": '',
                    "product": item['item_name'],
                    "productdescription": item['item_code'],
                    "parent": item['item_group'],
                    "partno": "",
                    "productgodown": item['warehouse'],
                    "unit": item['uom'],
                    "Altunit": "",
                    "productqty": item['qty'],
                    "productAltqty": "",
                    "productrate": item['rate'],
                    "producthsn": item['gst_hsn_code'],
                    "productigstpercentage": "",
                    "productcgstpercentage": "",
                    "productsgstpercentage": "",
                    "taxamount": '',
                    "taxableamount": "",
                    "productvalue": item['net_amount']
                }
                
                sales_invoice_list[invoice['sales_invoice']]['saleslist'][0]['vchproductlist'].append(item_dict)
                # i=i+1
            # for index, line_item in invoice.get('items', []):
            # #enumerate(invoice['items']):
            
            #                     "invoicenumber": "",
            #                     "product": invoice['item_code'],
            #                     "productdescription": '',
            #                     "parent": "",
            #                     "partno": "",
            #                     "productgodown": "",
            #                     "unit": "SET",
            #                     "Altunit": "",
            #                     "productqty": invoice['qty'],
            #                     "productAltqty": "",
            #                     "productrate": invoice['rate'],
            #                     "producthsn": "",
            #                     "productigstpercentage": "18",
            #                     "productcgstpercentage": "9",
            #                     "productsgstpercentage": "9",
            #                     "taxamount": "",
            #                     "taxableamount": "",
            #                     "productvalue": invoice['grand_total']
                                
            #                 })
            # Assuming you have defined the 'invoice' dictionary and the 'item_dict' somewhere before this code snippet.
            # Import the necessary modules from Frappe

            # for item in purchase_invoices:
            #     item_dict = {
            #         "invoicenumber": invoice['sales_invoice'],
            #         "product": item['item_code'],
            #         "productdescription": item['item_name'],
            #         "parent": "",
            #         "partno": "",
            #         "productgodown": item['warehouse'],
            #         "unit": item['uom'],
            #         "Altunit": "",
            #         "productqty": item['qty'],
            #         "productAltqty": "",
            #         "productrate": item['rate'],
            #         "producthsn": "",
            #         "productigstpercentage": "18",
            #         "productcgstpercentage": "9",
            #         "productsgstpercentage": "9",
            #         "taxamount": item['total_taxes_and_charges'],
            #         "taxableamount": "",
            #         "productvalue": item['grand_total']
            #     }
            #     sales_invoice_list[invoice['sales_invoice']]['saleslist'][0]['vchproductlist'].append(item_dict)
            # for item in purchase_invoices:
            #     item_dict = {
            #         "invoicenumber": invoice['sales_invoice'],
            #         "product": item['item_code']
            #     }
            # for entry in sales_invoice_list[invoice['sales_invoice']]['saleslist']:
            #     entry['vchproductlist'].append(item_dict.copy())
            # Assuming you have defined the 'purchase_invoices', 'invoice', and 'sales_invoice_list' somewhere before this code snippet.
            # purchase_invoices = [
            #     {'item_code': 'item001'},
            #     {'item_code': 'item002'}
            # ]

# Assuming you have initialized 'sales_invoice_list' with the correct structure

# Loop through the purchase_invoices and add each item to the 'vchproductlist'
            # filtered_invoices = [item for item in purchase_invoices if item['parent'] == invoice['sales_invoice']]
            # item_dicts = [
            #     {"invoicenumber": invoice['sales_invoice'], "product": invoice['parent']} for item in purchase_invoices
            # ]

            # for entry in sales_invoice_list[invoice['sales_invoice']]['saleslist']:
            #     entry['vchproductlist'].extend(item_dicts)


# The sales_invoice_list should now contain the updated data.





# The sales_invoice_list now contains the updated data.

            
            # return susales_invoice_list.values()
    return sales_invoice_list.values()
    # return {
    #     "message": "Documents created",
    #     "created": sales_invoice_list
    # }

@frappe.whitelist(allow_guest=True)
def get_purchase_invoice():
    

    invoice_names = frappe.get_all("Purchase Invoice", fields=["name"])

    purchase_invoice_list = []

    for invoice_name in invoice_names:
        invoice_name = invoice_name['name']
        
        # Fetch the Purchase Invoice document
        invoice = frappe.get_doc("Purchase Invoice", invoice_name)

        # Fetch related Purchase Invoice Items
        items = frappe.get_all("Purchase Invoice Item",
                            filters={"parent": invoice_name},
                            fields=["item_code", "item_name", "description", "item_group", 
                                    "qty", "stock_qty", "uom", "stock_uom", "conversion_factor",
                                    "rate", "base_rate", "stock_uom_rate", "amount", "base_amount", 
                                    "expense_account", "warehouse", "cost_center", 
                                    "item_tax_template", "base_price_list_rate", 
                                    "discount_percentage", "price_list_rate"])

        # Fetch related taxes
        taxes = frappe.get_all("Purchase Taxes and Charges",
                            filters={"parent": invoice_name},
                            fields=["charge_type", "row_id", "account_head", "base_tax_amount",
                                    "description", "cost_center", "tax_amount", 
                                    "tax_amount_after_discount_amount", "base_tax_amount_after_discount_amount",
                                    "base_total", "rate as Percent_Rate"])

        # Convert items and taxes to required format
        item_data = [{
            "item_code": item.item_code,
            "item_name": item.item_name,
            "description": item.description,
            "item_group": item.item_group,
            "qty": str(item.qty),
            "stock_qty": str(item.stock_qty),
            "uom": item.uom,
            "stock_uom": item.stock_uom,
            "conversion_factor": str(item.conversion_factor),
            "rate": str(item.rate),
            "base_rate": str(item.base_rate),
            "stock_uom_rate": str(item.stock_uom_rate),
            "amount": str(item.amount),
            "base_amount": str(item.base_amount),
            "expense_account": item.expense_account,
            "warehouse": item.warehouse,
            "cost_center": item.cost_center,
            "selling_price_list": "",
            "item_tax_template": "",
            "base_price_list_rate": str(item.base_price_list_rate),
            "discount_percentage": str(item.discount_percentage),
            "price_list_rate": str(item.price_list_rate)
        } for item in items]

        tax_data = [{
            "charge_type": tax.charge_type,
            "row_id": "",
            "account_head": tax.account_head,
            "base_tax_amount": str(tax.base_tax_amount),
            "description": tax.description,
            "cost_center": tax.cost_center,
            "tax_amount": str(tax.tax_amount),
            "tax_amount_after_discount_amount": str(tax.tax_amount_after_discount_amount),
            "base_tax_amount_after_discount_amount": str(tax.base_tax_amount_after_discount_amount),
            "base_total": str(tax.base_total),
            "Percent_Rate": str(tax.Percent_Rate)
        } for tax in taxes]

        # Prepare the data structure for this invoice
        invoice_data = {
            "doctype": invoice.doctype,
            "naming_series": invoice.naming_series,
            "InvoiceMode": "Invoice Voucher View",
            "supplier": invoice.supplier,
            "Invoice_value": str(invoice.grand_total),
            "company": invoice.company,
            "posting_date": invoice.posting_date.strftime('%d-%m-%Y'),
            "posting_time": invoice.posting_time,
            "due_date": invoice.due_date.strftime('%d-%m-%Y'),
            "currency": invoice.currency,
            "base_total": str(invoice.base_grand_total),
            "gst_category": invoice.gst_category,
            "credit_to": invoice.credit_to,
            "remarks": invoice.remarks,
            "webstatus_docname1": "NA",  # Example static value, replace with actual if needed
            "tally_masterid": "",  # Example static value, replace with actual if needed
            "tally_voucherno": invoice_name,
            "set_posting_time": str(flt(invoice.set_posting_time)),
            "is_return": str(flt(invoice.is_return)),
            "bill_no": invoice.bill_no,
            "bill_date": invoice.bill_date.strftime('%d-%m-%Y') if invoice.bill_date else '',
            "taxes_and_charges": invoice.taxes_and_charges,
            "items": item_data,
            "taxes": tax_data
        }

        purchase_invoice_list.append(invoice_data)

    # Prepare the final data structure
    return  {"data": purchase_invoice_list}

@frappe.whitelist(allow_guest=True)
def get_purchase_invoice3():
    invoice_names = frappe.get_all("Purchase Receipt", fields=["name"])

    purchase_invoice_list = []

    for invoice_name in invoice_names:
        invoice_name = invoice_name['name']
        
        # Fetch the Purchase Receipt document
        invoice = frappe.get_doc("Purchase Receipt", invoice_name)

        # Fetch related Purchase Receipt Items
        items = frappe.get_all("Purchase Receipt Item",
                            filters={"parent": invoice_name},
                            fields=["item_code", "item_name", "description", "item_group", 
                                    "qty", "stock_qty", "uom", "stock_uom", "conversion_factor",
                                    "rate", "base_rate", "stock_uom_rate", "amount", "base_amount", 
                                    "expense_account", "warehouse", "cost_center", 
                                    "item_tax_template", "base_price_list_rate", 
                                    "discount_percentage", "price_list_rate"])

        # Fetch related taxes
        taxes = frappe.get_all("Purchase Taxes and Charges",
                            filters={"parent": invoice_name},
                            fields=["charge_type", "row_id", "account_head", "base_tax_amount",
                                    "description", "cost_center", "tax_amount", 
                                    "tax_amount_after_discount_amount", "base_tax_amount_after_discount_amount",
                                    "base_total", "rate as Percent_Rate"])

        # Calculate total base amount of all items
        total_base_amount = sum(flt(item["base_amount"]) for item in items)

        # Convert items and taxes to required format
        item_data = []

        for item in items:
            # Calculate item-wise taxes proportionally
            item_taxes = []
            for tax in taxes:
                item_tax_amount = (flt(item["base_amount"]) / total_base_amount) * flt(tax["base_tax_amount"])
                item_taxes.append({
                    "item_tax": tax["account_head"],
                    "tax_amount": str(item_tax_amount)
                })

            item_info = {
                "item_code": item["item_code"],
                "item_name": item["item_name"],
                "description": item["description"],
                "item_group": item["item_group"],
                "qty": str(item["qty"]),
                "stock_qty": str(item["stock_qty"]),
                "uom": item["uom"],
                "stock_uom": item["stock_uom"],
                "conversion_factor": str(item["conversion_factor"]),
                "rate": str(item["rate"]),
                "base_rate": str(item["base_rate"]),
                "stock_uom_rate": str(item["stock_uom_rate"]),
                "amount": str(item["amount"]),
                "base_amount": str(item["base_amount"]),
                "expense_account": item["expense_account"],
                "warehouse": item["warehouse"],
                "cost_center": item["cost_center"],
                "selling_price_list": item.get("selling_price_list"),
                "item_tax_template": item["item_tax_template"],
                "base_price_list_rate": str(item["base_price_list_rate"]),
                "discount_percentage": str(item["discount_percentage"]),
                "price_list_rate": str(item["price_list_rate"]),
                "item_taxes": item_taxes  # Add item-wise taxes here
            }

            item_data.append(item_info)

        tax_data = [{
            "charge_type": tax["charge_type"],
            "row_id": tax.get("row_id"),
            "account_head": tax["account_head"],
            "base_tax_amount": str(tax["base_tax_amount"]),
            "description": tax["description"],
            "cost_center": tax["cost_center"],
            "tax_amount": str(tax["tax_amount"]),
            "tax_amount_after_discount_amount": str(tax["tax_amount_after_discount_amount"]),
            "base_tax_amount_after_discount_amount": str(tax["base_tax_amount_after_discount_amount"]),
            "base_total": str(tax["base_total"]),
            "Percent_Rate": str(tax["Percent_Rate"])
        } for tax in taxes]

        # Prepare the data structure for this invoice
        invoice_data = {
            "doctype": "Purchase Invoice",
            "naming_series": invoice.naming_series,
            "InvoiceMode": "Invoice Voucher View",
            "supplier": invoice.supplier,
            "Invoice_value": str(invoice.grand_total),
            "company": invoice.company,
            "posting_time": invoice.posting_time,
            "currency": invoice.currency,
            "base_total": str(invoice.base_grand_total),
            "gst_category": invoice.gst_category,
            # "credit_to": invoice.credit_to,
            "remarks": invoice.remarks,
            "webstatus_docname1": "NA",  # Example static value, replace with actual if needed
            "tally_masterid": "",  # Example static value, replace with actual if needed
            "tally_voucherno": invoice_name,
            # "bill_no": invoice.bill_no,
            "taxes_and_charges": invoice.taxes_and_charges,
            "items": item_data,
            "taxes": tax_data
        }

        purchase_invoice_list.append(invoice_data)

    # Prepare the final data structure
    data = {"data": purchase_invoice_list}
    frappe.response['message'] = data

@frappe.whitelist(allow_guest=True)
def get_purchase_invoice1():
    query = """
        SELECT pi.name, pi.supplier, pi.posting_date, pi.grand_total, pii.item_code,pii.item_name, pii.qty, pii.rate
    FROM `tabPurchase Invoice` pi
    INNER JOIN `tabPurchase Invoice Item` pii ON pi.name = pii.parent"""

    purchase_invoices = frappe.db.sql(query, as_dict=True)

    purchase_invoice_list = {}
    for invoice in purchase_invoices:
        if invoice['name'] not in purchase_invoice_list:
            print(purchase_invoices)
            # buyer_address = invoice['address_display']
            # buyer_dtls = buyer_address.split("<br>")

            purchase_invoice_list[invoice['name']] = {
                "tallycode": "111999",
                "tallyname": "MADRAS TUBULAR RIVETS",
                "tallyserialno": "725688774",
                "salesguid": "85a6e8ef-044b-482b-8ee5-0ea3b1d302eb-00000017",
                "ipaddress": "192.23.453",
                "systemname": "Lenova Laptop",
                "createduser": "Windows User",
                "requesttype": "PURCHASE",
                "purchaselist":
                [{
                    'invoicenumber': invoice['name'],
                    'invoicedate': invoice['posting_date'].strftime('%d-%m-%Y'),
                    "narration": "",
                    'customername': invoice['supplier'],
                    "vchtype": "Purchase",
                    "invoicemode": "Invoice Voucher View",
                    "reference": "2074/22-23",
                    "salesledger": "Purchase Account",
                    "vchclass": "",
                    "deliverynoteno": "",
                    "deliverynotedate": "",
                    "dispatchdocno": "",
                    "dipatchthrough": "",
                    "destination": "",
                    "lrrnumber": "",
                    "lrrdate": "",
                    "vehiclenumber": "TN64J6468",
                    "ordernumber": "28220125",
                    "orderdate": "27-09-2022",
                    "modeofpayment": "",
                    "otherreference": "",
                    "termsofdelivery": "",
                    "buyername": invoice['supplier'],
                    "buyeraddress1": "",
                    "buyeraddress2": "TSK PURAM KANJAMANAICKENPATTI MUSTAKURICHI P.O VIRUDHUNAGAR DISTRICTTAMILNADU.",
                    "buyeraddress3": " ",
                    "buyeraddress4": " ",
                    "buyeraddress5": "",
                    "country": "",
                    "buyerstate": "",
                    "placeofsupply": "Tamil Nadu",
                    "buyergstinnumber": "",
                    "deliveryname": "SUNDARAM BRAKE LININGS LIMITED ( TSK - I )",
                    "deliveryaddress1": "SUNDARAM BRAKE LININGS LIMITED TSK PLANT - 1",
                    "deliveryaddress2": "TSK PURAM KANJAMANAICKENPATTI MUSTAKURICHI P.O VIRUDHUNAGAR DISTRICTTAMILNADU.",
                    "deliveryaddress3": " ",
                    "deliveryaddress4": " ",
                    "deliveryaddress5": "",
                    "consigneestate": "Tamil Nadu",
                    "consigneegstinnumber": "33AADCS4888E1Z8",
                    "subvalue": "",
                    "roundoffledger": "Rounding Off",
                    "roundoffamount": "",
                    "invoicevalue": invoice['grand_total'],
                    "irn": "",
                    "ackno":"",
                    "ackdate": "",
                    "SignedInvoice": "",
                    "SignedQRCode":"",
                    "ewaybillno": "",
                    "ewaybillnodate": "",
                    # 'grand_total': invoice['grand_total'],
                    # 'outstanding_amount': invoice['outstanding_amount'],
                    "vchproductlist_pur": [],
                    "vchledgerlist_pur": [
                        {
                            "invoicenumber": invoice['name'],
                            "additionalledger": "Output  CGST @ 9%",
                            "parent": "",
                            "rateofpercentage": "",
                            "additionalledgervalue": ""
                        },
                        {
                            "invoicenumber": invoice['name'],
                            "additionalledger": "Output  SGST @ 9%",
                            "parent": "",
                            "rateofpercentage": "",
                            "additionalledgervalue": ""
                        }
                    ]
                }
                ]}
            purchase_invoice_list[invoice['name']]['purchaselist'][0]['vchproductlist_pur'].append({
                "invoicenumber": "",
                "product": invoice['item_code'],
                "productdescription": invoice['name'],
                "parent": "",
                "partno": "",
                "productgodown": "",
                "unit": "SET",
                "Altunit": "",
                "productqty": invoice['qty'],
                "productAltqty": "",
                "productrate": invoice['rate'],
                "producthsn": "",
                "productigstpercentage": "18",
                "productcgstpercentage": "9",
                "productsgstpercentage": "9",
                "taxamount": "",
                "taxableamount": "",
                "productvalue": invoice['grand_total']
            })

            # return supurchase_invoice_list.values()
    return purchase_invoice_list.values()


# Get Masters based on Request type 

@frappe.whitelist(allow_guest=True)
def getmasters(*args,**kwargs):       
    # Requested data
    
    data = {"tallycode": "111999",
    "tallyname": "",
    "tallyserialno": "756563",
    "requesttype": "UOM" ,
    "webcode":"111999"
    }   
    # data = frappe.form_dict
    
    # tallycode = data.get('tallycode')
    # tallyname = data.get('tallyname')
    # tallyserialno = data.get('tallyserialno')
    # requesttype = data.get('requesttype')
    # webcode = data.get('webcode')
    tallyserialno = kwargs.get('tallyserialno')
    tallycode = kwargs.get('tallycode')
    tallyname = kwargs.get('tallyname')
    requesttype = kwargs.get('requesttype')
    
    master = {}
    customer_list = []
    item_list = []
    uom_list = []
    
   #ledger
    if requesttype == "LEDGER":
            customers_record = """
            
                SELECT *
                FROM `tabCustomer` 
            """
            suppliers_record = """ 
                SELECT *  FROM `tabSupplier`
                """
            customers = frappe.db.sql(customers_record, as_dict=True)
            suppliers = frappe.db.sql(suppliers_record,as_dict = True)
            master['tallycode'] = tallycode
            master['tallyname'] = tallyname
            master['tallyserialno'] = tallyserialno
            master['requesttype'] = requesttype
            for customer in customers: 
                if customer.customer_primary_address is not None:
                    customer_primary_address = frappe.get_doc('Address',customer.customer_primary_address)
                    address1= customer_primary_address.address_line1,
                    state = customer_primary_address.state,
                    pincode= customer_primary_address.pincode 
                    customer_dict = {
                        'ledgername':'',
                        'ledgercode':customer.customer_name,
                        'ledgergroup':customer.customer_group,
                        'ledgermailing':customer.email_id,
                        'ledgeraddress':address1[0],
                        'ledgercountry':customer.territory,
                        'ledgerstate': '',
                        'ledgerpincode':pincode,
                        'ledgermobile':customer.mobile_no,
                        'ledgeremail':customer.email_id,
                        'ledgergstin':'',
                        'ledgerpan':'',
                        'ledgerregtype':'',
                        'ledgeraccountholder':customer.customer_name,
                        'ledgeraccountno':'',
                        'ledgerifsc':'',
                        'ledgerbank':'',
                        'ledgerbranch':'',              
                        'ledgertaxability':'',
                        'ledgerhsn':'',
                        'ledgerigst':'',
                        'ledgercgst':'',
                        'ledgersgst':'',
                        'ledgercess':'',
                        'ledgertypesupply':'',
                        'ledgertaxhead':'',
                        'ledgertypeoftax':customer.tax_category,
                        'ledgertaxpercentage':'',
                        'ledgercreditperiod':'',
                        'ledgercreditlimit':'',
                        'ledgerguid':'',
                        'ipaddress':'',
                        'systemname':'',
                        'createduser':'',
                        }
                    customer_list.append(customer_dict)
            for supplier in suppliers:
                if supplier.supplier_primary_address is not None:
                    supplier_address_instance = frappe.get_doc('Address',supplier.supplier_primary_address)
                    address1 = supplier_address_instance.address_line1
                    state = supplier_address_instance.state
                    pincode = supplier_address_instance.pincode
                    supplier_dict = {
                    "ledgername": supplier.supplier_name,
                    'ledgercode':supplier.supplier_name,
                    'ledgergroup':supplier.supplier_group,
                    'ledgermailing':supplier.email_id,
                    'ledgeraddress':address1,
                    'ledgercountry':supplier.country,
                    'ledgerstate':state.title(),
                    'ledgerpincode':pincode,
                    'ledgermobile':supplier.mobile_no,
                    'ledgeremail':supplier.email_id,
                    'ledgergstin':'',
                    'ledgerpan':'',
                    'ledgerregtype':'',
                    'ledgeraccountholder':supplier.supplier_name,
                    'ledgeraccountno':'',
                    'ledgerifsc':'',
                    'ledgerbank':supplier.default_bank_account,
                    'ledgerbranch':'',               
                    'ledgertaxability':'',
                    'ledgerhsn':'',
                    'ledgerigst':'',
                    'ledgercgst':'',
                    'ledgersgst':'',
                    'ledgercess':'',
                    'ledgertypesupply':'',
                    'ledgertaxhead':'',
                    'ledgertypeoftax':'',
                    'ledgertaxpercentage':'',
                    'ledgercreditperiod':'',
                    'ledgercreditlimit':'',
                    'ledgerguid':'',
                    'ipaddress':'',
                    'systemname':'',
                    'createduser':''    
                    }
                    customer_list.append(supplier_dict)
            master['ledgerlist'] = customer_list        
            
    elif requesttype == "PRODUCT":
            items_record  = """
            SELECT * 
            FROM `tabItem` 
            """
            items = frappe.db.sql(items_record, as_dict = True) 
            master['tallycode'] = tallycode
            master['tallyname'] = tallyname
            master['tallyserialno'] = tallyserialno
            master['requesttype'] = requesttype 
            for item in items:
                items_dict = {
                'productname':item.item_name,
                'productcode':'',
                'productgroup':item.item_group,  
                'productpartno':"",
                'productdescription':item.description,
                'productuom': item.stock_uom,
                'productAltuom': "",
                'productAltuomValue': "",
                'productuomValue': "",
                'productgst': "",
                'producthsn': "",
                'producttaxable': "",
                'productigst': "",
                'productcgst': "",
                'productsgst': "",
                'productcess': "",
                'productsellingdetails': {
                'sellingdate': "",
                'sellingrate': ""
                },
                'productcostdetails': {
                'costdate': "",
                'costrate': ""
                },
                'productgroupguid': ""
                }
                item_list.append(items_dict)
            master["productlist"] =  item_list  
              
    elif requesttype == "UOM":
            uoms_record  = """
            SELECT * FROM  `tabUOM`
            """
            uoms = frappe.db.sql(uoms_record,as_dict = True)
            master['tallycode'] = tallycode
            master['tallyname'] = tallyname
            master['tallyserialno'] = tallyserialno
            master['requesttype'] = requesttype
            for uom in uoms:
                uom_dict = {
                'uomname': uom.uom_name,
                'uomcode':uom.uom_name,
                'uomshortcode':'',
                'uomdecimals':'',
                'uomguid':'',
                'ipaddress':'',
                'systemname':'',
                'createduser':''
                }
                uom_list.append(uom_dict)
            master['uomlist'] = uom_list               
    return  master
