from buidl.tx import TxIn, TxOut, Tx
from buidl.script import ScriptPubKey, address_to_script_pubkey

class BeaconManager():

    def __init__(self, bitcoin_rpc, network, beacon_id, signing_key, script_pubkey):
        self.bitcoin_rpc = bitcoin_rpc
        self.network = network
        self.beacon_id = beacon_id
        self.signing_key = signing_key
        self.script_pubkey = script_pubkey
        self.address = script_pubkey.address(network)
        self.utxos = self.fetch_utxos()

        

    def fetch_utxos(self):
        # TODO: get UTXOs for address
        print("TODO")
        return []

    def add_funding_tx(self, funding_tx):
        print("Adding funding TX")
        for index, tx_out in enumerate(funding_tx.tx_outs):
            print(self.address, tx_out.script_pubkey.address(network=self.network))
            if self.address == tx_out.script_pubkey.address(network=self.network):
                print("Found funding TXOUT")
                tx_in = TxIn(prev_tx=funding_tx.hash(), prev_index=index)
                tx_in._script_pubkey = tx_out.script_pubkey
                tx_in._value = tx_out.amount
                self.utxos.append(tx_in)

    def construct_beacon_signal(self, commitment_bytes):
        if len(self.utxos) == 0:
            raise Exception("No UTXOs, fund beacon")
        
        tx_in = self.utxos.pop(0)

        script_pubkey = ScriptPubKey([0x6a, commitment_bytes])

        beacon_signal_txout = TxOut(0, script_pubkey)

        tx_fee = 350

        refund_amount = tx_in.value() - tx_fee

        refund_script_pubkey = self.script_pubkey
        refund_out = TxOut(amount=refund_amount, script_pubkey=refund_script_pubkey)
        tx_ins = [tx_in]

        tx_outs = [beacon_signal_txout, refund_out]
        pending_beacon_signal = Tx(version=1, tx_ins=tx_ins, tx_outs=tx_outs, network=self.network,segwit=True)

        new_utxo_txin = TxIn(prev_tx=pending_beacon_signal.hash(), prev_index=1)
        new_utxo_txin._script_pubkey = refund_out.script_pubkey
        new_utxo_txin._value = refund_out.amount
        self.utxos.append(new_utxo_txin)

        return pending_beacon_signal

    def sign_beacon_signal(self, pending_signal):

        signing_res = pending_signal.sign_input(0, self.signing_key)
        print(signing_res)
        if not signing_res:
            raise Exception("Invalid Beacon Key, unable to sign signal")
        
        return pending_signal

    # TODO: only works on regtest
    async def fund_beacon_address(self):
        result = await self.bitcoin_rpc.acall("send", {"outputs": { self.address: 0.2}})

        funding_txid = result["txid"]
        funding_tx_hex = await self.bitcoin_rpc.acall("getrawtransaction", {"txid": funding_txid})
        funding_tx = Tx.parse_hex(funding_tx_hex)
        
        self.add_funding_tx(funding_tx)