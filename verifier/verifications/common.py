from starkware.crypto.signature.fast_pedersen_hash import pedersen_hash
from starkware.crypto.signature.signature import sign


def generate_signature(token_id_low, token_id_high, field, data, private_key):
    hash = pedersen_hash(
        pedersen_hash(pedersen_hash(token_id_low, token_id_high), field), data
    )
    signed = sign(hash, private_key)
    return signed


class WrongRequestException(Exception):
    pass


class BlockchainDiffersFromProof(Exception):
    pass
