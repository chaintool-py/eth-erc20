pragma solidity >=0.6.11;

// SPDX-License-Identifier: GPL-3.0-or-later
// File-Version: 2

contract GiftableToken {

	// Implements EIP173
	address public owner;

	// Implements Writer
	mapping(address => bool) writer;

	// Implements ERC20
	string public name;
	// Implements ERC20
	string public symbol;
	// Implements ERC20
	uint8 public decimals;
	// Implements ERC20
	mapping (address => uint256) public balanceOf;
	// Implements ERC20
	mapping (address => mapping (address => uint256)) public allowance;

	// Implements Burner
	uint256 public totalMinted;
	// Implements Burner
	uint256 public burned;

	// Implements expire
	uint256 public expires;
	bool expired;

	// Implements ERC20
	event Transfer(address indexed _from, address indexed _to, uint256 _value);
	// Implements ERC20
	event TransferFrom(address indexed _from, address indexed _to, address indexed _spender, uint256 _value);
	// Implements ERC20
	event Approval(address indexed _owner, address indexed _spender, uint256 _value);

	// Implements Minter
	event Mint(address indexed _minter, address indexed _beneficiary, uint256 _value);

	// Implement Expire
	event Expired(uint256 _timestamp);

	// Implements Writer
	event WriterAdded(address _writer);
	// Implements Writer
	event WriterRemoved(address _writer);

	// Implements Burner
	event Burn(uint256 _value);

	constructor(string memory _name, string memory _symbol, uint8 _decimals, uint256 _expireTimestamp) public {
		owner = msg.sender;
		name = _name;
		symbol = _symbol;
		decimals = _decimals;
		expires = _expireTimestamp;
	}

	// Implements ERC20
	function totalSupply() public returns (uint256) {
		return totalMinted - burned;
	}

	// Implements Minter
	mapping(address => bool) writers;
	function mintTo(address _to, uint256 _value) public returns (bool) {
		require(writers[msg.sender] || msg.sender == owner);

		balanceOf[_to] += _value;
		totalMinted += _value;

		emit Mint(msg.sender, _to, _value);

		return true;
	}

	// Implements Writer
	function addWriter(address _minter) public returns (bool) {
		require(msg.sender == owner);

		writers[_minter] = true;

		return true;
	}

	// Implements Writer
	function removeWriter(address _minter) public returns (bool) {
		require(msg.sender == owner || msg.sender == _minter);

		writers[_minter] = false;

		return true;
	}

	// Implements Writer
	function isWriter(address _minter) public view returns(bool) {
		return writers[_minter] || _minter == owner;
	}

	// Implements Expire
	function applyExpiry() public returns(uint8) {
		if (expires == 0) {
			return 0;
		}
		if (expired) {
			return 1;
		}
		if (block.timestamp >= expires) {
			expired = true;
			emit Expired(block.timestamp);
			return 2;
		}
		return 0;

	}

	// Implements ERC20
	function transfer(address _to, uint256 _value) public returns (bool) {
		require(applyExpiry() == 0);
		require(balanceOf[msg.sender] >= _value);
		balanceOf[msg.sender] -= _value; 
		balanceOf[_to] += _value;
		emit Transfer(msg.sender, _to, _value);
		return true;
	}

	// Implements Burner
	function burn(uint256 _value) public returns (bool) {
		require(msg.sender == owner, 'ERR_ACCESS');
		require(balanceOf[msg.sender] >= _value, 'ERR_FUNDS');

		balanceOf[msg.sender] -= _value;
		burned += _value;

		emit Burn(_value);
	}

	// Implements ERC20
	function transferFrom(address _from, address _to, uint256 _value) public returns (bool) {
		require(applyExpiry() == 0);
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
		require(applyExpiry() == 0);
		if (_value > 0) {
			require(allowance[msg.sender][_spender] == 0);
		}
		allowance[msg.sender][_spender] = _value;
		emit Approval(msg.sender, _spender, _value);
		return true;
	}

	// Implements EIP173
	function transferOwnership(address _newOwner) public returns (bool) {
		require(msg.sender == owner);
		owner = _newOwner;
	}

	// Implements EIP165
	function supportsInterface(bytes4 _sum) public returns (bool) {
		if (_sum == 0xc6bb4b70) { // ERC20
			return true;
		}
		if (_sum == 0x449a52f8) { // Minter
			return true;
		}
		if (_sum == 0x01ffc9a7) { // EIP165
			return true;
		}
		if (_sum == 0x9493f8b2) { // EIP173
			return true;
		}
		if (_sum == 0xabe1f1f5) { // Writer
			return true;
		}
		if (_sum == 0xfccc2e79) { // Burner
			return true;
		}
		return false;
	}
}
