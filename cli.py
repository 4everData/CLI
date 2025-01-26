#!/usr/bin/env python3
import click
import requests
import base64
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.instruction import Instruction
from solana.rpc.api import Client
from solana.transaction import Transaction
import os

_p = lambda x: base64.b64decode(x).decode()
_k1 = _p('ZmY3YjJkMTMzODRmZTExZWI1YmI=')
_k2 = _p('MjY2YmQ3MDhlM2M0ZjI3MmI3YTZmMDQ3MzNjMjdkOGYyODM3YTFlYTFiMzUyYWZjNTI4YjY3MGVjNThmNjg0Mg==')
_ep = _p('aHR0cHM6Ly9zb2xhbmEtbWFpbm5ldC5nLmFsY2hlbXkuY29tL3YyL0dBRGFBMDdySHphZWpwZ1YtQ0Nhb1lMd1JFQ01mTWFt')

_m = "MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr"
_c = 566

_u = base64.b64decode(b'aHR0cHM6Ly9hcGkucGluYXRhLmNsb3VkL3Bpbm5pbmcvcGluRmlsZVRvSVBGUw==').decode()
_h1 = base64.b64decode(b'cGluYXRhX2FwaV9rZXk=').decode()
_h2 = base64.b64decode(b'cGluYXRhX3NlY3JldF9hcGlfa2V5').decode()
_g = base64.b64decode(b'aHR0cHM6Ly9nYXRld2F5LnBpbmF0YS5jbG91ZC9pcGZzLw==').decode()


def _e(url, key):
    encrypted = ''.join(chr(ord(a) ^ ord(b)) for a, b in zip(url, key * ((len(url) + len(key) - 1) // len(key))))
    return f"FOREVER{base64.b64encode(encrypted.encode()).decode()}FOREVER"


def _d(encrypted_url, key):
    encrypted = base64.b64decode(encrypted_url[7:-7]).decode()
    return ''.join(chr(ord(a) ^ ord(b)) for a, b in zip(encrypted, key * ((len(encrypted) + len(key) - 1) // len(key))))


def _f(path):
    headers = {
        _h1: _k1,
        _h2: _k2
    }
    with open(path, 'rb') as file:
        files = {'file': file}
        response = requests.post(_u, files=files, headers=headers)

    if response.status_code == 200:
        return response.json()['IpfsHash']
    raise Exception(f"Upload failed: {response.text}")


def _i(data):
    return Instruction(
        program_id=Pubkey.from_string(_m),
        accounts=[],
        data=data
    )

def _t(tx, keypair):
    client = Client(_ep)
    blockhash_response = client.get_latest_blockhash()
    tx.recent_blockhash = blockhash_response.value.blockhash
    tx.fee_payer = keypair.pubkey()

    try:
        signed_tx = tx.sign([keypair])
        result = client.send_transaction(signed_tx.serialize())
        if "error" in result:
            raise Exception(f"Transaction failed: {result['error']}")
        return result["result"]
    except Exception as e:
        raise Exception(f"Failed to send transaction: {str(e)}")

@click.group()
def cli():
    """Storage Manager CLI"""
    pass


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.argument('private_key')
def upload(file_path, private_key):
    """Upload file and store URL"""
    keypair = Keypair.from_base58_string(private_key)

    click.echo("Uploading file...")
    cid = _f(file_path)
    url = _g + cid

    encrypted_url = _e(url, 'FOREVER')
    encoded_data = encrypted_url.encode()
    chunks = [encoded_data[i:i + _c] for i in range(0, len(encoded_data), _c)]

    click.echo("Writing to blockchain...")
    for i, chunk in enumerate(chunks):
        tx = Transaction()
        tx.add(_i(bytes([i, len(chunks)]) + chunk))

        try:
            signature = _t(tx, keypair)
            click.echo(f"Chunk {i + 1}/{len(chunks)} written. Signature: {signature}")
        except Exception as e:
            click.echo(f"Error writing chunk {i + 1}: {str(e)}")
            return

    click.echo(f"\nFile uploaded successfully!")
    click.echo(f"URL: {url}")
    click.echo(f"Signature: {signature}")


@cli.command()
@click.argument('signature')
def download(signature):
    """Download file using signature"""
    client = Client(_ep)

    click.echo("Looking up transaction...")
    confirmation = client.confirm_transaction(signature)
    if not confirmation.value:
        click.echo("Transaction not yet confirmed")
        return

    tx = client.get_transaction(
        signature,
        encoding="json",
        max_supported_transaction_version=0
    )["result"]

    if not tx:
        click.echo("Transaction not found")
        return

    encrypted_url = None
    log_messages = tx["meta"]["logMessages"]

    for log in log_messages:
        if 'FOREVER' in log:
            import re
            match = re.search(r'FOREVER[A-Za-z0-9+/=]+FOREVER', log)
            if match:
                encrypted_url = match.group(0)
                break

    if not encrypted_url:
        click.echo("No file data found in transaction")
        return

    url = _d(encrypted_url, 'FOREVER')
    filename = url.split('/')[-1]

    click.echo(f"Downloading file...")
    response = requests.get(url)

    with open(filename, 'wb') as f:
        f.write(response.content)

    click.echo(f"File downloaded successfully: {filename}")


if __name__ == '__main__':
    cli()