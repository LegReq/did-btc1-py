from buidl.tx import TxIn, Tx, TxOut
from buidl.script import address_to_script_pubkey
from buidl.helpers import hex_to_bytes

class AddressManager():

    def __init__(self, esplora_client, network, script_pubkey, signing_key):
        self.esplora_client = esplora_client
        self.network = network
        self.script_pubkey = script_pubkey
        self.address = script_pubkey.address(network)
        self.signing_key = signing_key
        self.utxo_tx_ins = self.fetch_utxos()

    def get_address(self, address):
        return self.esplora_client.get_address(address)
    
    def fetch_utxos(self):
        utxos = self.esplora_client.get_address_utxos(self.address)
        tx_ins = []
        for utxo in utxos:
            txid = utxo["txid"]
            prev_index = utxo["vout"]
            txin = TxIn(prev_tx=hex_to_bytes(txid), prev_index=prev_index)
            txin._script_pubkey = self.script_pubkey
            txin._value = utxo["value"]
            tx_ins.append(txin)
            # txin.serialize()
        print(f"Found {len(utxos)} UTXOs for {self.address}")
        return tx_ins
    
    def add_funding_tx(self, funding_tx):
        print("Adding funding TX")
        for index, tx_out in enumerate(funding_tx.tx_outs):
            print(self.address, tx_out.script_pubkey.address(network=self.network))
            if self.address == tx_out.script_pubkey.address(network=self.network):
                print("Found funding TXOUT")
                tx_in = TxIn(prev_tx=funding_tx.hash(), prev_index=index)
                tx_in._script_pubkey = tx_out.script_pubkey
                tx_in._value = tx_out.amount
                self.utxo_tx_ins.append(tx_in)
    
    def send_to_address(self, address, amount):
        tx_fee = 350
        if len(self.utxo_tx_ins) == 0:
            raise Exception(f"No UTXOs, fund address {self.address}")
        
        tx_ins = []
        total_value = 0
        for utxo in self.utxo_tx_ins:
            total_value += utxo.value()
            if total_value >= amount + tx_fee:
                break
        
        if total_value >= amount + tx_fee:
            raise Exception(f"Address does not control enough value to cover {amount}, fund address {self.address}")
        

        txout = TxOut(amount=amount, script_pubkey=address_to_script_pubkey(address))
        refund_out = TxOut(amount=total_value - amount - tx_fee, script_pubkey=self.script_pubkey)
        tx = Tx(version=1, tx_ins=tx_ins, tx_outs=[txout, refund_out], network=self.network, segwit=True)

        for index in range(len(tx_ins)):
            tx.sign_input(index, self.signing_key)

        tx_hex = tx.serialize().hex()
        tx_id = self.esplora_client.broadcast_tx(tx_hex)
        print(f"Sent {amount} to {address} with txid {tx_id}")
        self.utxo_tx_ins = self.fetch_utxos()
        return tx_id