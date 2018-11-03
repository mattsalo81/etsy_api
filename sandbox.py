#!/home/syrup/anaconda3/envs/etsy3/bin/python

from etsy_py.api import EtsyAPI
import requests
import pprint
import re
import authentication
import secrets

pp = pprint.PrettyPrinter(indent=2)
app_permissions = ['transactions_r']


def main():
    (api_key, client_secret) = secrets.get_secrets();

    shop_id = 'PlannerBunnyPress'
    api = EtsyAPI(api_key=api_key)
    auth = authentication.get_oauth(api, api_key, client_secret, app_permissions)

    print("getting all receipts...");
    receipts = get_unsatisfied_receipts(api, auth, shop_id)
    print("getting all transactions...");
    transactions = get_transactions_for_receipts(api, auth, receipts)
    transactions = remove_digital_printable_transactions(transactions)

    pick_list = {}
    print("looking through transactions...");
    for transaction in transactions:
        item = make_item_type_for_transaction(transaction)
        pick_list[item] = pick_list.setdefault(item, 0) + transaction['quantity']

    pp.pprint(pick_list)

def remove_digital_printable_transactions(transactions):
    """returns a list of transactions identical to the first, with all transactions removed
    with /printable/i or /digital/i in the title"""
    cleaned_transactions = [];
    for transaction in transactions:
        if (re.match('printable', transaction['title'], flags=re.IGNORECASE)):
            next
        if (re.match('digital', transaction['title'], flags=re.IGNORECASE)):
            next
        cleaned_transactions.append(transaction)
    return cleaned_transactions

def make_item_type_for_transaction(transaction):
    variation_objects = transaction['variations']
    variations = {}
    for variation_object in variation_objects:
        name  = variation_object['formatted_name']
        value = variation_object['formatted_value']
        variations[name] = value
    item = transaction['title']

    # get rid of everything after the first '|'
    item = item.split('|', 1)[0]
    
    for name in sorted(variations.keys()):
        value = variations[name]
        item += f"  '{name}'='{value}'"

    return item

def get_unsatisfied_receipts(api, auth, shop_id):
    receipts = get_all_results(api, auth, f'/shops/{shop_id}/receipts', {'was_paid':1,'was_shipped':0})
    return receipts

def get_transactions_for_receipts(api, auth, receipts):
    transactions = []
    for receipt in receipts:
        receipt_id = receipt['receipt_id']
        trans4receipt = get_all_results(api, auth, f'/receipts/{receipt_id}/transactions', {})
        transactions.extend(trans4receipt);
    return transactions

def get_all_results(api, auth, base_url, context):
    limit = 100
    offset = 0
    results = []

    user_parameters = ''
    for parm, value in context.items():
        user_parameters += f'&{parm}={value}'

    while True:
        url = base_url + f'?limit={limit}&offset={offset}' + user_parameters 

        r = api.get(url, auth=auth)
        offset += limit
        r = r.json()["results"]
        if (len(r) == 0):
            break
        results.extend(r)
    return results

main()
