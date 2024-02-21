// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

//
// Author: Marko Dimitrijevic
// This smart contract stores VRPs and allows for the reconstruction of the newest snapshot added to it
//

//
// Regarding this implementation:
// This smart contract does not allow for the editing of already existing VRPs.
// It implements getter and adder functions
// It is intended that VRPBase is filled with the first snapshot of any VRP set intended to be stored.
//

contract VRPManager {

    // ##########  Structures  ##########
    // Address of the creator of the smart contract
    // Only the maintainer is allowed to add VRPs to this contract
    address maintainer;

    // VRP Entry
    // Basic entry to store all relevant VRP data
    struct VRPEntry {
        uint32 asn;
        string ipPrefix;
        uint8 maxLength;
        //NOTE: ipPrefix in this implementation is stored as a string and allows for storage of IPV4/6 prefixes
        //If only IPv4 prefixes are stored, then bytes32 allows for a more efficient solution
    }

    // VRPBase
    // Stores every VRP that is used as the base snapshot
    struct VRPBase {
        // size: amount of VRPs added to VRPBase
        uint32 size;
        // base: mapping that stores an incrementing list of VRPs
        // base[i]: ith VRP stored in base
        mapping(uint32 => VRPEntry) base;
    }

    // DeltaSeries
    // Stores all Deltas since the base snapshot in chronological order
    struct DeltaSeries {
        // size: amount of Deltas added to DeltaSeries
        uint32 size;
        // deltaVRPMap: nested map that emulates a list of Delta files
        // deltaVRPMap[i][0][j]: the jth VRP entry contained in the add list of the ith delta
        // deltaVRPMap[i][1][j]: the jth VRP entry contained in the remove list of the ith delta
        mapping(uint32 => mapping(uint8 => mapping(uint32 => VRPEntry))) deltaVRPMap;
        // delta: mapping that stores the sizes of the add/remove lists contained in the Deltas
        // deltaSizes[i][0]: the size of the add list in the ith delta
        // deltaSizes[i][1]: the size of the remove list in the ith delta
        mapping(uint32 => mapping(uint8 => uint32)) deltaSizes;
    }

    // ##########  Objects  ##########
    // Here the two objects are created for use in the following functions
    VRPBase public vrpBase;
    DeltaSeries public deltaSeries;

    // ##########  Events  ##########
    //Event called once the creation of the VRPBase is finished
    event BaseFinal(address indexed owner, uint32 indexed size);

    //Event called once DeltaSeries contains a new Delta
    event DeltaUpdate(address indexed owner, uint32 indexed size);

    // ##########  Ownership initialization  ##########
    //At the initialization of the contract, the sender is saved as the maintainer
    constructor(){
        maintainer = msg.sender;
    }

    //Modifier used to limit certain function calls to maintainer
    modifier validated(){
        require(msg.sender == maintainer);
        _;
    }

    // ##########  Functions  ##########

    // ##########  Base  ##########

    //Fetches a VRP from the base snapshot
    //index: index of the VRP
    function getBaseVRP(uint32 index) view external returns (VRPEntry memory){
        return vrpBase.base[index];
    }

    function getBaseSize() view external returns (uint32){
        return vrpBase.size;
    }

    // Adds a new ROA entry to the base snapshot
    // _asn: ASN of the new VRP
    // _ipPrefix: ip prefix of the new VRP
    // _maxLength: maxLength parameter of the new VRP
    function addBaseVRP(uint32 _asn, string calldata _ipPrefix, uint8 _maxLength) external validated {
        // Add the new ROA entry
        vrpBase.base[vrpBase.size] = VRPEntry({
            asn: _asn,
            ipPrefix: _ipPrefix,
            maxLength: _maxLength
        });
        vrpBase.size++;
    }
    // Broadcasts an event to signal a finalized base snapshot
    function bcastVRPS() external validated {
        emit BaseFinal(msg.sender, vrpBase.size);
    }

    // ##########  Deltas  ##########

    //Get amount of Deltas contained in DeltaSeries
    function getDeltaCount() external view returns (uint32){
        return deltaSeries.size;
    }

    //Get amount of entries contained in an add/remove list of a specified delta
    //deltaIndex: index of the Delta from which to gather
    //addBool: False = get entry count of remove list; True = get entry count of remove list
    function getDeltaEntryCount(uint32 deltaIndex, bool addBool) external view returns (uint32){
        if (addBool) {
            return deltaSeries.deltaSizes[deltaIndex][0];
        }
        else {
            return deltaSeries.deltaSizes[deltaIndex][1];
        }
    }

    //Get a specific VRP from VRPSeries
    //deltaIndex: Index of specific Delta
    //vrpIndex: Index of specific Delta
    //addBool: False = get entry count of remove list; True = get entry count of remove list
    function getDeltaVRPEntry(uint32 deltaIndex, uint32 vrpIndex, bool addBool) external view returns (VRPEntry memory){
        if (addBool) {
            return deltaSeries.deltaVRPMap[deltaIndex][0][vrpIndex];
        }
        else {
            return deltaSeries.deltaVRPMap[deltaIndex][1][vrpIndex];
        }
    }

    // Increase size of DeltaSeries by adding a new Delta to the mapping
    // This method has to be invoked before adding any elements of a new delta
    // Once invoked, previous delta cannot receive new entries
    function addNewDelta() external validated {
        //Initialize new list sizes
        deltaSeries.deltaSizes[deltaSeries.size][0] = 0;
        deltaSeries.deltaSizes[deltaSeries.size][1] = 0;
        //Add new delta by incrementing delta count
        deltaSeries.size++;
    }

    // Add a new VRP to the newest Delta in the DeltaSeries
    // toAdd - 0: VRP to RemoveList, 1: VRP to AddList
    // _asn - VRP ASN to add
    // _ipPrefix - VRP IP Prefix to add
    // _maxLength - VRP maxLength Prefix to add
    function addDeltaVRP(bool toAdd, uint32 _asn, string calldata _ipPrefix, uint8 _maxLength) external validated {
        //VRP to be added
        if (toAdd) {
            deltaSeries.deltaVRPMap[deltaSeries.size - 1][0][deltaSeries.deltaSizes[deltaSeries.size - 1][0]] = VRPEntry({
                asn: _asn,
                ipPrefix: _ipPrefix,
                maxLength: _maxLength
            });
            deltaSeries.deltaSizes[deltaSeries.size - 1][0]++;
        }
            //VRP to be removed
        else {
            deltaSeries.deltaVRPMap[deltaSeries.size - 1][1][deltaSeries.deltaSizes[deltaSeries.size - 1][1]] = VRPEntry({
                asn: _asn,
                ipPrefix: _ipPrefix,
                maxLength: _maxLength
            });
            deltaSeries.deltaSizes[deltaSeries.size - 1][1]++;
        }
    }

    //Function to announce a new Delta in DeltaSeries
    function bcastDeltaUpdate() external validated {
        emit DeltaUpdate(msg.sender, deltaSeries.size);
    }

}