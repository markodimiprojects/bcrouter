__author__ = "Marko Dimitrijevic, 7633863"

import json

from web3 import Web3
import os
from dotenv import load_dotenv

"""
@author: Marko Dimitrijevic, 7633863

This class is responsible for fetching data from the Routinator connection
"""


class blockchainHandler:

    def __init__(self):
        """
        Initialize the blockchain handler and establish a connection
        """

        # Access data from .env
        load_dotenv()
        # Node access URL
        self.node_url = os.getenv("NODE_URL_TEST")
        # Address of contract on the blockchain
        self.contract_address = os.getenv("CONTRACT_ADDRESS_TEST")
        # Address of user
        self.caller = os.getenv("CALLER_TEST")
        # Private key of user to sign transactions
        # MUST MATCH MAINTAINER TO ADD TO BLOCKCHAIN
        self.private_key = os.getenv("PRIVATE_KEY_TEST")

        # Initialize web3 interaction handler and relevant data
        self.web3 = Web3(Web3.HTTPProvider(self.node_url))

        # Get smart contract functions
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
        """
        Get amount of VRPs in baseVRP
        :return: size (Amount of Elements in baseVRP)
        :rtype: Int
        """
        try:
            return self.contract.functions.getBaseSize().call()
        except Exception as e:
            print("Error fetching baseVRP size: " + str(e))

    def getDeltaVRP(self, deltaIndex, vrpIndex, toAdd):
        """
        Get specified delta VRP
        :param deltaIndex: Index of delta
        :type deltaIndex: Int
        :param vrpIndex: Index of VRP in specified delta
        :type vrpIndex: Int
        :param toAdd: Boolean to specify list (False - Remove List; True - Add List)
        :type toAdd: Bool
        :return: Delta VRP
        :rtype: Dict
        """
        try:
            return self.contract.functions.getDeltaVRPEntry(deltaIndex, vrpIndex, toAdd).call()
        except Exception as e:
            print("Error fetching specified delta VRP: " + str(e))

    def getDeltaCount(self):
        """
         Get amount of deltas in deltaSeries
        :return: size (Amount of Elements in deltaSeries)
        :rtype: Int
        """
        try:
            return self.contract.functions.getDeltaCount().call()
        except Exception as e:
            print("Error fetching delta count: " + str(e))

    def getDeltaEntryCount(self, index, addBool):
        """
        Get amount of entries contained in an Add/Remove list of a specified delta
        :param index: Delta Index
        :type index: int
        :param addBool: List specifier Boolean (False - Remove List; True - Add List)
        :type addBool: Bool
        :return: Amount of VRPs contained in specifed list
        :rtype: int
        """
        try:
            return self.contract.functions.getDeltaEntryCount(index, addBool).call()
        except Exception as e:
            print("Error fetching delta entry count: " + str(e))

    def addNewDelta(self):
        """
        Adds a new Delta entry to the Delta series
        """
        try:
            while True:  # Retries necessary for parallel uploading of deltas and base snapshot
                call = self.contract.functions.addNewDelta().build_transaction(
                    {"chainId": self.chain_id, "from": self.caller, "nonce": self.nonce})
                signed_tx = self.web3.eth.account.sign_transaction(call, private_key=self.private_key)
                send_tx = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
                tx_receipt = self.web3.eth.wait_for_transaction_receipt(send_tx)
                # print(tx_receipt)  # Optional
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
            while True:  # Retries necessary for parallel uploading of deltas and base snapshot
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
        Add a delta to the blockchain from a given delta JSON
        :param deltaJSON: JSON containing data
        :type deltaJSON: Dict
        """
        # Add a new delta entry before adding deltas
        self.addNewDelta()

        json_add = deltaJSON["announced"]
        json_rmv = deltaJSON["withdrawn"]

        for vrp in json_add:  # Add data from add list
            asn = vrp["asn"][2::]  # Remove characters from ASN
            ipPrefix = vrp["prefix"]
            maxLength = vrp["maxLength"]
            self.addDeltaVRP(True, int(asn), ipPrefix, maxLength)
        for vrp in json_rmv:  # Add data from remove list
            asn = vrp["asn"][2::]
            ipPrefix = vrp["prefix"]
            maxLength = vrp["maxLength"]
            self.addDeltaVRP(False, int(asn), ipPrefix, maxLength)

    def addAllBaseVRPS(self, baseJSON):
        """
        Adds a base snapshot from data contained in a JSON file
        :param baseJSON: Base snapshot in JSON format
        :type baseJSON: Dict
        """
        json_vrps = baseJSON["roas"]

        for vrp in json_vrps:  # Adds all base VRPS
            asn = vrp["asn"][2::]  # Remove characters from ASN
            ipPrefix = vrp["prefix"]
            maxLength = vrp["maxLength"]
            self.addBaseVRP(int(asn), ipPrefix, maxLength)

    def getBaseSnapshot(self):
        """
        Fetches the base snapshot from the blockchain
        :return: Base snapshot
        :rtype: Dict
        """
        baseSize = self.getBaseSize()
        snapshot = []

        for i in range(baseSize):  # Fetch every VRP
            vrp = self.getBaseVRP(i)
            snapshot.append(vrp)
        return snapshot

    def applyDeltas(self, snapshot):
        """
        Applies the deltas to a base snapshot in chronological order
        :param snapshot: base snapshot
        :type snapshot: Dict
        :return: snapshot with deltas applied
        :rtype: Dict
        """
        deltaCount = self.getDeltaCount()
        for i in range(deltaCount):  # Delta loop
            addcount = self.getDeltaEntryCount(i, True)
            rmvcount = self.getDeltaEntryCount(i, False)
            for j in range(addcount):  # Delta add loop
                snapshot.append(self.getDeltaVRP(i, j, True))
            for k in range(rmvcount):  # Delta remove loop
                snapshot.remove(self.getDeltaVRP(i, k, False))

    def getNewestSnapshot(self):
        """
        Fetch the newest snapshot from the blockchain
        :return: Most recent snapshot
        :rtype: Dict
        """
        snapshot = self.getBaseSnapshot()
        self.applyDeltas(snapshot)
        finalDict = {"roas": []}  # Build json structure to be used by RTRTR
        for vrp in snapshot:
            finalDict["roas"].append({"asn": "AS" + vrp[0], "prefix": vrp[1], "maxLength": vrp[2],
                                      "ta": "bc"})  # Trust anchor not stored, therefore bc (blockchain) is denoted
        return finalDict
