import json
import time

from web3 import Web3
import os
from dotenv import load_dotenv


class blockchainHandler:

    def __init__(self):
        """
        Initialize the blockchain handler and establish a connection
        """

        # Access data from .env
        load_dotenv()
        # Node access point
        self.node_url = os.getenv("NODE_URL_TEST")
        # Address of contract on the blockchain
        self.contract_address = os.getenv("CONTRACT_ADDRESS_TEST")
        # Address of user
        self.caller = os.getenv("CALLER_TEST")
        # Private key to sign transactions
        self.private_key = os.getenv("PRIVATE_KEY_TEST")

        # Initialize web3 interaction handler and relevant data
        self.web3 = Web3(Web3.HTTPProvider(self.node_url))

        with open("Metadata.json") as f:
            info_json = json.load(f)
        self.abi = info_json["abi"]

        self.contract = self.web3.eth.contract(address=self.contract_address, abi=self.abi)
        self.nonce = self.web3.eth.get_transaction_count(self.caller)
        self.chain_id = self.web3.eth.chain_id

    def updateNonce(self):
        """
        Updates the nonce value
        """
        self.nonce = self.web3.eth.get_transaction_count(self.caller, "pending")

    def getBaseVRP(self, index):
        """
        Get a specific base VRP
        :param index: Index position of the VRP in an array
        :type index: int
        """
        return self.contract.functions.getBaseVRP(index).call()

    def addBaseVRP(self, asn, ipPrefix, maxLength):
        """
        Add a VRP to the BaseVRP list
        :param asn: ASN of VRP
        :type asn: int
        :param ipPrefix: IP prefix of VRP
        :type ipPrefix: string
        :param maxLength: maxLength of VRP
        :type maxLength: int
        """
        try:
            while True:
                call = self.contract.functions.addBaseVRP(asn, ipPrefix, maxLength).build_transaction(
                    {"chainId": self.chain_id,
                     "from": self.caller,
                     # "gasPrice": int(self.web3.eth.gas_price * 1.4),
                     "nonce": (self.web3.eth.get_transaction_count(self.caller, "pending"))})
                signed_tx = self.web3.eth.account.sign_transaction(call, private_key=self.private_key)
                send_tx = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
                tx_receipt = self.web3.eth.wait_for_transaction_receipt(send_tx)
                # print(tx_receipt)  # Optional
                self.updateNonce()
                return
        except Exception as e:
            print("Error uploading base VRP (retrying): " + str(e))


    def getBaseSize(self):
        return self.contract.functions.getBaseSize().call()

    def getDeltaVRP(self, deltaIndex, vrpIndex, toAdd):
        return self.contract.functions.getDeltaVRPEntry(deltaIndex, vrpIndex, toAdd).call()

    def getDeltaCount(self):
        return self.contract.functions.getDeltaCount().call()

    def getDeltaEntryCount(self, index, addBool):
        return self.contract.functions.getDeltaEntryCount(index, addBool).call()

    def addNewDelta(self):
        """
        Adds a new Delta entry to the Delta series
        """
        try:
            while True:
                call = self.contract.functions.addNewDelta().build_transaction(
                    {"chainId": self.chain_id, "from": self.caller, "nonce": self.nonce})
                signed_tx = self.web3.eth.account.sign_transaction(call, private_key=self.private_key)
                send_tx = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
                tx_receipt = self.web3.eth.wait_for_transaction_receipt(send_tx)
                #print(tx_receipt)  # Optional
                self.updateNonce()
                return
        except Exception as e:
            print("Error uploading delta VRP (retrying): " + str(e))

    def addDeltaVRP(self, toAdd, asn, ipPrefix, maxLength):
        """
        Adds a Delta VRP to the newest delta in Delta series

        :param toAdd: Add to Announce/Revoke list: True - Add, False - Revoke
        :type toAdd: Bool
        :param asn: ASN of VRP
        :type asn: int
        :param ipPrefix: IP prefix of VRP
        :type ipPrefix: string
        :param maxLength: maxLength of VRP
        :type maxLength: int
        """
        try:
            while True:
                call = self.contract.functions.addDeltaVRP(toAdd, asn, ipPrefix, maxLength).build_transaction(
                    {"chainId": self.chain_id, "from": self.caller, "nonce": self.nonce})
                signed_tx = self.web3.eth.account.sign_transaction(call, private_key=self.private_key)
                send_tx = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
                tx_receipt = self.web3.eth.wait_for_transaction_receipt(send_tx)
                # print(tx_receipt)  # Optional
                self.updateNonce()
                return
        except Exception as e:
            print("Error uploading new Delta page (retrying): " + str(e))

    def addDelta(self, deltaJSON):
        """
        Add a Delta to deltaSeries from a JSON
        """
        # Add a new delta entry before adding deltas
        self.addNewDelta()

        json_add = deltaJSON["announced"]
        json_rmv = deltaJSON["withdrawn"]

        for vrp in json_add:  # Add data from add list
            asn = vrp["asn"][2::]  # Remove characters from ASN
            ipPrefix = vrp["prefix"]
            maxLength = vrp["maxLength"]
            # print("Adding: AS%s, Prefix: %s, maxLength: %s" % (str(asn), ipPrefix, str(maxLength)))
            self.addDeltaVRP(True, int(asn), ipPrefix, maxLength)
        for vrp in json_rmv:  # Add data from remove list
            asn = vrp["asn"][2::]
            ipPrefix = vrp["prefix"]
            maxLength = vrp["maxLength"]
            # print("Adding: AS%s, Prefix: %s, maxLength: %s" % (str(asn), ipPrefix, str(maxLength)))
            self.addDeltaVRP(False, int(asn), ipPrefix, maxLength)

    def addAllBaseVRPS(self, baseJSON):
        """
        Adds all VRPs from JSON to baseVRP
        """
        json_roas = baseJSON["roas"]

        for vrp in json_roas:  # Adds all base VRPS
            asn = vrp["asn"][2::]
            ipPrefix = vrp["prefix"]
            maxLength = vrp["maxLength"]
            #print("Adding: AS%s, Prefix: %s, maxLength: %s" % (str(asn), ipPrefix, str(maxLength)))
            self.addBaseVRP(int(asn), ipPrefix, maxLength)

    def getBaseSnapshot(self):
        baseSize = self.getBaseSize()
        snapshot = []
        for i in range(baseSize):
            vrp = self.getBaseVRP(i)
            snapshot.append(vrp)
        return snapshot

    def applyDeltas(self, snapshot):
        deltaCount = self.getDeltaCount()
        for i in range(deltaCount):
            addCount = self.getDeltaEntryCount(i, True)
            rmvCount = self.getDeltaEntryCount(i, False)
            for j in range(addCount):
                snapshot.append(self.getDeltaVRP(i, j, True))
            for k in range(rmvCount):
                snapshot.remove(self.getDeltaVRP(i, k, False))

    def getNewestSnapshot(self):
        snapshot = self.getBaseSnapshot()
        self.applyDeltas(snapshot)
        finalDict = {"roas": []}
        for vrp in snapshot:
            finalDict["roas"].append({"asn": vrp[0], "prefix": vrp[1], "maxLength": vrp[2], "ta": "bc"})

        return json.dumps(finalDict)

