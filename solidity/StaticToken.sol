pragma solidity >=0.8.0;

// SPDX-License-Identifier: AGPL-3.0-or-later

contract StaticToken {

	address owner;
	mapping(address => bool) minters;

	// Implements ERC20
	string public name;
	// Implements ERC20
	string public symbol;
	// Implements ERC20
	uint8 public decimals;
	// Implements ERC20
	uint256 public totalSupply;
	// Implements ERC20
	mapping (address => uint256) public balanceOf;
	// Implements ERC20
	mapping (address => mapping (address => uint256)) public allowance;

	// Implements ERC20
	event Transfer(address indexed _from, address indexed _to, uint256 _value);
	// Implements ERC20
	event TransferFrom(address indexed _from, address indexed _to, address indexed _spender, uint256 _value);
	// Implements ERC20
	event Approval(address indexed _owner, address indexed _spender, uint256 _value);

	constructor(string memory _name, string memory _symbol, uint8 _decimals, uint256 _supply) {
		owner = msg.sender;
		name = _name;
		symbol = _symbol;
		decimals = _decimals;
		totalSupply = _supply;
		balanceOf[owner] = _supply;
	}

	// Implements ERC20
	function transfer(address _to, uint256 _value) public returns (bool) {
		require(balanceOf[msg.sender] >= _value);
		balanceOf[msg.sender] -= _value; 
		balanceOf[_to] += _value;
		emit Transfer(msg.sender, _to, _value);
		return true;
	}

	// Implements ERC20
	function transferFrom(address _from, address _to, uint256 _value) public returns (bool) {
		require(allowance[_from][msg.sender] >= _value);
		require(balanceOf[_from] >= _value);
		allowance[_from][msg.sender] = allowance[_from][msg.sender] - _value;
		balanceOf[_from] -= _value; 
		balanceOf[_to] += _value;
		emit TransferFrom(_from, _to, msg.sender, _value);
		return true;
	}

	// Implements ERC20
	function approve(address _spender, uint256 _value) public returns (bool) {
		if (_value > 0) {
			require(allowance[msg.sender][_spender] == 0);
		}
		allowance[msg.sender][_spender] = _value;
		emit Approval(msg.sender, _spender, _value);
		return true;
	}

	// Implements EIP165
	function supportsInterface(bytes4 _sum) public pure returns (bool) {
		if (_sum == 0xb61bc941) { // ERC20
			return true;
		}
		if (_sum == 0x01ffc9a7) { // EIP165
			return true;
		}
		return false;
	}
}
