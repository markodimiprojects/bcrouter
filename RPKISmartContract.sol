// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VRPManager {

    // ##########  Structures  ##########

    address maintainer;

    // VRP Entry
    struct VRPEntry {
        uint32 asn;
        string ipPrefix;
        uint8 maxLength;
    }

    // Delta file - all VRPs to add/remove
    struct Delta {
        uint16 addSize;
        uint16 rmvSize;
        VRPEntry[] addVRP;
        VRPEntry[] rmvVRP;
    }

    // Store all VRPs for start
    struct VRPBase {
        uint32 size;
        mapping(uint32 => VRPEntry) base;
    }

    // Stores all Deltas in order
    struct DeltaSeries {
        uint32 size;
        mapping(uint32 => mapping (uint8 => mapping (uint32 => VRPEntry))) deltaVRPMap;
        mapping(uint32 => mapping (uint8 => uint32)) deltaSizes;
    }

    // ##########  Objects  ##########
    VRPBase public vrpBase;
    DeltaSeries public deltaSeries;


    // ##########  Events  ##########
    event BaseFinal(address indexed owner, uint32 indexed size);

    event DeltaUpdate(address indexed owner, uint32 indexed size);


    // ##########  Ownership initialization  ##########
    constructor() public{
      maintainer = msg.sender;
    }

    modifier validated(){
      require(msg.sender == maintainer);
      _;
    }

    // ##########  Functions  ##########

    // ##########  Base  ##########
    function getBaseVRP(uint32 index) view external returns (VRPEntry memory){
        return vrpBase.base[index];
    }

    // Function to add a new ROA entry
    function addBaseVRP( uint32 _asn, string memory _ipPrefix, uint8 _maxLength) external validated{

        // Add the new ROA entry

        vrpBase.base[vrpBase.size] = VRPEntry({
            asn: _asn,
            ipPrefix: _ipPrefix,
            maxLength: _maxLength
        });
        vrpBase.size++;
    }

    function bcastVRPS() external validated{
        emit BaseFinal(msg.sender, vrpBase.size);
    }

    // ##########  Deltas  ##########

    //Get amount of Deltas
    function getDeltaCount() external view returns (uint32){
        return deltaSeries.size;
    }

    //Get amount of add/remove entries in specified delta
    function getDeltaEntryCount(uint32 version, bool addBool) external view returns (uint32){
        if(addBool){
            return deltaSeries.deltaSizes[version][0];
        }
        else{
            return deltaSeries.deltaSizes[version][1];
        }
    }

    function getDeltaVRPEntry(uint32 deltaIndex, uint32 vrpIndex, bool addBool) external view returns (VRPEntry memory){
        if(addBool){
            return deltaSeries.deltaVRPMap[deltaIndex][0][vrpIndex];
        }
        else{
            return deltaSeries.deltaVRPMap[deltaIndex][1][vrpIndex];
        }
    }


    function addNewDelta() external validated{
        deltaSeries.deltaSizes[deltaSeries.size][0] = 0;
        deltaSeries.deltaSizes[deltaSeries.size][1] = 0;
        deltaSeries.size++;
    }

    // Add a new VRP to the newest Delta in the DeltaSeries
    // toAdd - 0: VRP to RemoveList, 1: VRP to AddList
    // _asn - VRP ASN to add
    // _ipPrefix - VRP IP Prefix to add
    // _maxLength - VRP maxLength Prefix to add
    function addDeltaVRP(bool toAdd, uint32 _asn, string memory _ipPrefix, uint8 _maxLength) external validated{
        //VRP to be added
        if(toAdd){
            deltaSeries.deltaVRPMap[deltaSeries.size-1][0][deltaSeries.deltaSizes[deltaSeries.size-1][0]] = VRPEntry({
            asn: _asn,
            ipPrefix: _ipPrefix,
            maxLength: _maxLength
            });
            deltaSeries.deltaSizes[deltaSeries.size-1][0]++;
        }
        //VRP to be removed
        else{
            deltaSeries.deltaVRPMap[deltaSeries.size-1][1][deltaSeries.deltaSizes[deltaSeries.size-1][1]] = VRPEntry({
            asn: _asn,
            ipPrefix: _ipPrefix,
            maxLength: _maxLength
            });
            deltaSeries.deltaSizes[deltaSeries.size-1][1]++;
        }
    }

    //Function to announce a Delta update
    function bcastDeltaUpdate() external validated{
        emit DeltaUpdate(msg.sender, deltaSeries.size);
    }
}
// Missing getBaseSize