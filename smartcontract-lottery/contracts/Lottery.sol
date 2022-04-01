// SPDX-License-Identifier: MIT

pragma solidity ^0.6.6;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";

// since we are doing above imports, we need to add dependencies in brownie-config.yaml

// Ownable comes with openzeppelin
contract Lottery is VRFConsumerBase, Ownable {
    // below is to keep track of all the players
    address payable[] public players;
    address payable public recentWinner;
    uint256 public usdEntryFee;
    uint256 public randomness; // to keep track of the most recent random number
    AggregatorV3Interface internal ethUsdPriceFeed;

    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    // enum type to represent lottery state, elements are numbered as 0, 1, 2
    // now we can create a type of lottery_state
    LOTTERY_STATE public lottery_state;

    event RequestedRandomness(bytes32 requestId);

    uint256 public fee; // fee is the link token needed to pay for the request
    // since this can change from blockchain to blockchain, we will add this in constructor as well
    bytes32 public keyhash; // keyhash is a way to uniquely identify the chainlink vrf node

    // since we use AggregatorV3Interface, we need to import this from chainlink as below pragma solidity
    // we can use a constructor from imported/inherited contract in our constructor by typing after public below
    // any additional constructor from inherited contracts
    constructor(
        // below are basically what we need to deploy this contract
        address _priceFeedAddress, // passing price feed address
        address _vrfCoordinator, // _vrfCoordinator is the onchain contract that checks numbers are truly random
        address _link, // _link is the chainlink token as a payment to the chain of its services
        // above addresses are gonna change based on the blockchain we are on, which make sense to parameterize them
        uint256 _fee, // fee is the link token needed to pay for the request
        bytes32 _keyhash
    ) public VRFConsumerBase(_vrfCoordinator, _link) {
        // we'd like to parameterize price feed mechanism
        // we pass the address of price feed as constructor parameter
        usdEntryFee = 50 * (10**18);
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress); //here we passed the price feed address for conversion rate
        // right when we initiliaze our contract, we want lottery state to be closed
        lottery_state = LOTTERY_STATE.CLOSED; // since closed is represented by 1, we can also say lottery_state=1
        fee = _fee; // fee is how much we are gonna pay for delivering us this random number
        keyhash = _keyhash; // keyhash uniquely identifies the link node we are gonna use
    }

    // below function chould be payable since we want them to pay to enter
    function enter() public payable {
        require(lottery_state == LOTTERY_STATE.OPEN); //meaning we can only enter if somebody has started this lottery
        require(msg.value >= getEntranceFee(), "Not enough ETH!"); // we want players to put at least 50dollars
        players.push(msg.sender); // anytime somebody enters we push them to array
    }

    // below is to get entrance fee of the lottery
    // since we will just return a number for get entrance fee, view is used
    function getEntranceFee() public view returns (uint256) {
        //before getting anything we need to store 50 dollars somewhere
        // after having price feed "ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);" we can set up entrance fee

        (, int256 price, , , ) = ethUsdPriceFeed.latestRoundData();
        // to convert int256 to uint256
        uint256 adjustedPrice = uint256(price) * 10**10; // we know price from latestRoundData comes with 8 decimals,
        // so multiplying it wiht 10 deicmals make 18 decimals

        uint256 costToEnter = (usdEntryFee * 10**18) / adjustedPrice;
        return costToEnter;
        // to make sure of the above math here, early testing is important and recommended
    }

    // below could be called only by admin
    // we could either write our own onlyOwner modifier or we can use open zeppelins ownable contract functions
    function startLottery() public onlyOwner {
        require(
            lottery_state == LOTTERY_STATE.CLOSED, // to start the lottery we need it to be closed first
            "Can't start a new lottery yet!"
        );
        lottery_state = LOTTERY_STATE.OPEN;
    }

    // below is where we choose random winner
    // we only want admin to end the lottery, which brings onlyOwner modifier
    function endLottery() public onlyOwner {
        // below in this function we request the random number data from chainlink oracle
        lottery_state = LOTTERY_STATE.CALCULATING_WINNER; //while this happening, no other function can be called
        bytes32 requestId = requestRandomness(keyhash, fee); // this is built-in function of VRFConsumerBase
        // this will take keyhash and fee and return bytes32 called requestid
        emit RequestedRandomness(requestId);
    }

    function fulfillRandomness(bytes32 _requestId, uint256 _randomness)
        internal
        override
    {
        // in this function chainlink returns the data to this contract
        // we dont want anyone else to call this function except our chain link node, thats why we add internal
        // only the vrfcoordinator can call this function
        // override meaning that we are gonna override the original decleration of fulfillrandomness function
        // fullfilrandomness function is left laid out in vrfconsumerbase.sol, meant to be overriden by us, so we can override it
        require(
            lottery_state == LOTTERY_STATE.CALCULATING_WINNER,
            "You aren't there yet!"
        ); // lets first check if we are in the right state
        require(_randomness > 0, "random-not-found"); // to check if we got the response
        uint256 indexOfWinner = _randomness % players.length;
        // % is the mod function of _randomness against players.length
        recentWinner = players[indexOfWinner]; // this selected the winner based on the result of mod function
        recentWinner.transfer(address(this).balance); // this pays the gathered money from all of our entries
        // After money transfer, we wanna reset the lottery
        players = new address payable[](0); // (0) means array of size 0
        lottery_state = LOTTERY_STATE.CLOSED; // changing the lottery state
        randomness = _randomness; // to keep track of the most recent random number
    }
}
