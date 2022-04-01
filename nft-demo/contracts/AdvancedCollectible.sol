// making an nft where the token uri can be one of 3 different dogs and it is gonna be randomly selected

// An NFT Contract
// Where the tokenURI can be one of 3 different dogs
// Randomly selected

// SPDX-License-Identifier: MIT
pragma solidity 0.6.6;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol"; // to work with chanlink VRF to get random number

// creating contract
contract AdvancedCollectible is ERC721, VRFConsumerBase {
    // above is how we inherit all functions from ERC721 and VRFConsumerBase
    uint256 public tokenCounter;
    bytes32 public keyhash;
    uint256 public fee;

    // in order to get random dog, they need to be different from each other in some details
    // so below are some definition of what the different breeds dogos can be
    // our dogos will be one of those below breeds
    // once we get the random number, we will pick one of these
    enum Breed {
        PUG,
        SHIBA_INU,
        ST_BERNARD
    }
    mapping(uint256 => Breed) public tokenIdToBreed; // assigning tokenId to random breed by mapping
    mapping(bytes32 => address) public requestIdToSender; // assigning requestId as a key to msg.sender, who is calling the createCollectible function

    // best practice is to emit an event whenever we update a mapping
    // below we create an event for each mapping
    event requestedCollectible(bytes32 indexed requestId, address requester); // this will be emitted whenever we requestId to sender since we are updating the mapping
    event breedAssigned(uint256 indexed tokenId, Breed breed);

    // since we want to use below parameters working on different testnets and chains, we use vrfcoordinator constructor
    constructor(
        address _vrfCoordinator,
        address _linkToken,
        bytes32 _keyhash,
        uint256 _fee
    )
        public
        VRFConsumerBase(_vrfCoordinator, _linkToken)
        ERC721("Dogie", "DOG")
    {
        // Dogie, DOG and tokenCounter are for ERC721 and the rest is for VRFConsumerBase
        tokenCounter = 0;
        keyhash = _keyhash;
        fee = _fee;
    }

    // here we have a factory contract which produces certain type of NFT
    // below function helps people to create new NFTs assigned to them
    // creating new NFT is just mapping a tokenid to a new address

    function createCollectible() public returns (bytes32) {
        // we are returning requestId here
        bytes32 requestId = requestRandomness(keyhash, fee); // this is gonna create our randomness request to get a random breed for our dogs
        requestIdToSender[requestId] = msg.sender; // taking requestId as a key to msg.sender, who is calling the createCollectible function
        // above will later be used to call _safeMint
        emit requestedCollectible(requestId, msg.sender); // whenever update a mapping, best practice to emit an event
    }

    // below, in fullfillrandomness function we define how we are gonna pick random dogo
    // fulfillrandomness function is internal so that it is only called by VRFCoordinator
    // one the below function is done, breed of the dog is set
    function fulfillRandomness(bytes32 requestId, uint256 randomNumber)
        internal
        override
    {
        Breed breed = Breed(randomNumber % 3); // meaning "breed" variable is of type "Breed" equals to result of Breed enum
        uint256 newTokenId = tokenCounter; // tokenId is equal to tokencounter
        tokenIdToBreed[newTokenId] = breed; // assigning tokenId to random breed by mapping to keep track
        // above, this way each tokenId will have specific breed
        emit breedAssigned(newTokenId, breed);
        // below, since _safemint is only called by msg.sender and fulfillRandomness is only called by VRFCoordinator
        // we have to find a way to call _safeMint by the orginal caller of create collectible
        address owner = requestIdToSender[requestId]; // from requestIdToSender mapping we get the address of collectible creater
        _safeMint(owner, newTokenId);
        tokenCounter = tokenCounter + 1;
    }

    // below function sets the tokenURI based on the breed(tokenId)
    // tokenURI could even be decided by fulfillrandomness function for full decentralization
    function setTokenURI(uint256 tokenId, string memory _tokenURI) public {
        // we need three tokenURIs for pug, shiba inu, st bernard

        // we want only the owner of tokenId can update the tokenURI
        // below function is imported from OpenZeppelin contract and checks the owner of ERC721 of that tokenId
        // which makes only the owner or approved person can change tokenURI
        require(
            _isApprovedOrOwner(_msgSender(), tokenId),
            "ERC721: caller is not owner no approved"
        );

        // we can automatize the below function with another mapping at the top but left as here for tutorial purposes to call later
        _setTokenURI(tokenId, _tokenURI); // this function sets tokenURI to tokenid
        // this will allow our nft have an image for us to see
        // uri is just a unique resource identifier, like https, ipfs, any url pointing to a metadata
    }
}
