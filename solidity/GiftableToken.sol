pragma solidity >=0.6.12;

// SPDX-License-Identifier: GPL-3.0-or-later

contract GiftableToken {

	address owner;
	mapping(address => bool) minters;

	string public name;
	string public symbol;
	uint8 public decimals;
	uint256 public totalSupply;
	mapping (address => uint256) public balanceOf;
	mapping (address => mapping (address => uint256)) public allowances;

	event Transfer(address indexed _from, address indexed _to, uint256 _value);
	event TransferFrom(address indexed _from, address indexed _to, address indexed _spender, uint256 _value);
	event Approval(address indexed _owner, address indexed _spender, uint256 _value);

	constructor(string memory _name, string memory _symbol, uint8 _decimals) public {
		owner = msg.sender;
		name = _name;
		symbol = _symbol;
		decimals = _decimals;
		minters[msg.sender] = true;
	}

	function mint(uint256 _value) public returns (bool) {
		require(minters[msg.sender]);

		balanceOf[msg.sender] += _value;
		totalSupply += _value;

		return true;
	}

	function addMinter(address _minter) public returns (bool) {
		require(msg.sender == owner);

		minters[_minter] = true;

		return true;
	}

	function removeMinter(address _minter) public returns (bool) {
		require(msg.sender == owner || msg.sender == _minter);

		minters[_minter] = false;

		return true;
	}

	function transfer(address _to, uint256 _value) public returns (bool) {
		require(balanceOf[msg.sender] >= _value);
		balanceOf[msg.sender] -= _value; 
		balanceOf[_to] += _value;
		emit Transfer(msg.sender, _to, _value);
		return true;
	}

	function transferFrom(address _from, address _to, uint256 _value) public returns (bool) {
		require(allowances[_from][msg.sender] >= _value);
		require(balanceOf[_from] >= _value);
		allowances[_from][msg.sender] = allowances[_from][msg.sender] - _value;
		balanceOf[_from] -= _value; 
		balanceOf[_to] += _value;
		emit TransferFrom(_from, _to, msg.sender, _value);
		return true;
	}

	function approve(address _spender, uint256 _value) public returns (bool) {
		allowances[msg.sender][_spender] += _value;
		emit Approval(msg.sender, _spender, _value);
		return true;
	}
}
