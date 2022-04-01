// SPDX-License-Identifier: MIT
pragma solidity 0.6.6; // choosing solidity version

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

contract SimpleCollectible is ERC721 {
    // this is how we inherit all functions from ERC721
    uint256 public tokenCounter;

    constructor() public ERC721("Dogie", "DOG") {
        // Dogie is name and DOG is symbol
        tokenCounter = 0;
    }

    // here we have a factory contract which produces certain type of NFT
    // below function helps people to create new NFTs assigned to them
    // creating new NFT is just mapping a tokenid to a new address

    function createCollectible(
        string memory tokenURI // without the URI nobody would know what doggie would look like
    ) public returns (uint256) {
        uint256 newTokenId = tokenCounter;
        _safeMint(msg.sender, newTokenId); // _safeMint function is used to create new NFTs
        // above takes to address which is the owner of NFT, and tokenid which starts from 0, increament by 1 and all unique
        // _safeMint also checks if tokenid is already taken so we dont overwrite it
        _setTokenURI(newTokenId, tokenURI); // this function sets tokenURI to tokenid
        // this will allow our nft have an image for us to see
        // uri is just a unique resource identifier, like https, ipfs, any url pointing to a metadata
        tokenCounter = tokenCounter + 1;
        return newTokenId;
    }
}
