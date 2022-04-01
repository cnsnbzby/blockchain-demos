// SPDX-License-Identifier: GPL-3.0

//every time you call a function, you make a transaction or state change in blockchain, costing gas

pragma solidity ^0.6.0; //defining solidity version

// if there is red line under above code, solidity version can be picked under "compile using remote version" to fix

// pragma solidity >=0.6.0 <0.9.0; this says version is between these numbers
//switching between versions is good practice

contract SimpleStorage {
    //contract stands for the smart contract to be created
    // uint means unsigned integer, 256 means bit size of 256
    uint256 favnumber; //this initialize favnumber to 0, favnumber is in global scope, accessible by every function
    // this is zeroth index in contract simplestorage
    // any other variables after that will be first, second, third....

    //bool favbool = false;
    //string favstring = "string";
    //int256 favint = -5;
    //address favaddress = 0x7ef0AAEa465eae6D10191D2D105cB19e57957Bf4;
    //bytes32 favbytes = "cat";
    // above are possible type options, since weonly wanna store numbers in this example above ones are not used

    struct People {
        //struct allows creating new types, here have we new type People
        uint256 favnumber; //index 0 inside the struct
        string name; //index 1 inside the struct
        //string is a special type of array
    }

    People[] public people; //array is a way of storing a list or a group of some object
    //People[] array is the type of the variable, public defines the visibility, people is the name
    // this is a dynamic array because it could change its size
    //if we make it People[1], then the size is 1 and it can only take 1 people

    mapping(string => uint256) public nameToFavNum; //type mapping of string mapped to type uint256

    // public functions are called by anyone
    // external functions can only be called externally
    // internal functions can only be called internally
    // private functions are only visible in functions they are defined in
    // if none of above is set for state variable, then it will automaticlly called internal

    function store(uint256 _favnum) public {
        //this is a function called store to change favnumber
        //simplest form of a function
        favnumber = _favnum;
        // variables defined in a function are only usable in the function they are defined
    }

    //view and pure functions, which you dont have to make transactions on
    //we do not make a state change, just reading a state on blockchain
    //blues are view functions or state variables
    //pure functions are just making math but not saving anything
    //view means we are gonna read some state

    function retrieve() public view returns (uint256) {
        return favnumber;
    }

    function addperson(string memory _name, uint256 _favnumber) public {
        // memory means delete the variable after execution, storage means keep it
        people.push(People(_favnumber, _name)); //push adds new people/person to array
        //first people is the array and second is form of people struct
        nameToFavNum[_name] = _favnumber;
    }
}
