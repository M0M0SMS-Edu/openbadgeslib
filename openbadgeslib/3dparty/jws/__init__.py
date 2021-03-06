import json

from . import algos
from . import header
from . import utils
from .exceptions import *

##############
# public api #
##############
def sign(head, payload, key=None, is_json=False):
    data = {
        'key': key,
        'header': json.loads(head) if is_json else head,
        'payload': json.loads(payload) if is_json else payload,
        'signer': None
    }
    # TODO: re-evaluate whether to pass ``data`` by reference, or to copy and reassign
    header.process(data, 'sign')
    if not data['key']:
        raise MissingKey("Key was not passed as a param and a key could not be found from the header")
    if not data['signer']:
        raise MissingSigner("Header was processed, but no algorithm was found to sign the message")
    signer = data['signer']
    signature = signer(_signing_input(head, payload, is_json), key)
    return signature


def verify(head, payload, encoded_signature, key=None, is_json=False):
    data = {
        'key': key,
        'header': json.loads(head) if is_json else head,
        'payload': json.loads(payload) if is_json else payload,
        'verifier': None
    }
    # TODO: re-evaluate whether to pass ``data`` by reference, or to copy and reassign
    header.process(data, 'verify')
    if not data['key']:
        raise MissingKey("Key was not passed as a param and a key could not be found from the header")
    if not data['verifier']:
        raise MissingVerifier("Header was processed, but no algorithm was found to sign the message")
    verifier = data['verifier']
    signature = utils.from_base64(encoded_signature)
    return verifier(_signing_input(head, payload, is_json), signature, key)

# This function Verify an assertion block passed as parameter
def verify_block(msg, key=None):
    try:
        head_encoded, payload_encoded, signature_encoded = msg.split(b'.')
    except ValueError:
        # The block has an incorrect format.
        raise SignatureError()

    data = {
        'key': key,
        'header': utils.decode(head_encoded),
        'payload': utils.decode(payload_encoded),
        'verifier': None
    }
    # TODO: re-evaluate whether to pass ``data`` by reference, or to copy and reassign
    header.process(data, 'verify')
    if not data['key']:
        raise MissingKey("Key was not passed as a param and a key could not be found from the header")
    if not data['verifier']:
        raise MissingVerifier("Header was processed, but no algorithm was found to sign the message")
    verifier = data['verifier']
    signature = utils.from_base64(signature_encoded)
    return verifier(head_encoded + b'.' + payload_encoded, signature, key)

####################
# semi-private api #
####################
def _signing_input(head, payload, is_json=False):
    enc = utils.to_base64 if is_json else utils.encode
    head_input, payload_input = map(enc, [head, payload])
    return head_input + b'.' + payload_input
