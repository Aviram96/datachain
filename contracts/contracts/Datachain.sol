// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Datachain {
    struct VideoRecord {
        string cameraId;
        uint256 timestamp;
        string cid;
        address uploader;
    }

    // Mapping from Camera ID to an array of Video Records
    mapping(string => VideoRecord[]) private cameraVideos;

    event VideoStored(
        string indexed cameraId,
        uint256 timestamp,
        string cid,
        address indexed uploader
    );

    /**
     * @dev Anchors the IPFS CID of a 1-minute video chunk to the blockchain.
     * @param _cameraId Identifier for the CCTV camera
     * @param _timestamp Epoch time of the video recording
     * @param _cid IPFS Content Identifier
     */
    function storeVideoHash(
        string memory _cameraId,
        uint256 _timestamp,
        string memory _cid
    ) public {
        require(bytes(_cameraId).length > 0, "Camera ID cannot be empty");
        require(bytes(_cid).length > 0, "CID cannot be empty");

        VideoRecord memory newRecord = VideoRecord({
            cameraId: _cameraId,
            timestamp: _timestamp,
            cid: _cid,
            uploader: msg.sender
        });

        cameraVideos[_cameraId].push(newRecord);

        emit VideoStored(_cameraId, _timestamp, _cid, msg.sender);
    }

    /**
     * @dev Retrieves all video records for a specific camera.
     * @param _cameraId Identifier for the CCTV camera
     */
    function getVideosByCamera(string memory _cameraId) 
        public 
        view 
        returns (VideoRecord[] memory) 
    {
        return cameraVideos[_cameraId];
    }
}