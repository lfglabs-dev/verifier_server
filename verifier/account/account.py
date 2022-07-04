from starknet_py.contract import Contract
from starknet_py.net.account.account_client import AccountClient
from starknet_py.net.signer.stark_curve_signer import KeyPair
import json
import os


class Account:
    def __init__(self, conf):
        self.address = conf.starknet_address
        self.key = conf.starknet_key
        self.starknetid_contract = conf.starknetid_contract

    def get_path(self, name):
        return os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
            ),
            name,
        )

    async def load(self):
        self.client = AccountClient(
            net="testnet",
            address=self.address,
            key_pair=KeyPair.from_private_key(self.key),
        )
        with open(self.get_path("abi.json"), "r") as read_file:
            abi = json.load(read_file)
            self.contract = Contract(
                self.starknetid_contract,
                abi,
                self.client,
            )

    async def fetch_blockchain_id(self, nftid, type):
        result = await self.contract.functions["get_data"].call(nftid, type)
        return result.data

    async def confirm_validity(self, nftid, type, data):
        invocation = await self.contract.functions["confirm_validity"].invoke(
            nftid, type, data, max_fee=100_000_000_000_000
        )
        # await invocation.wait_for_acceptance()
        return invocation.hash
