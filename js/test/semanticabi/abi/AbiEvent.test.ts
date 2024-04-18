import {AbiEvent} from 'semanticabi/abi/item/AbiEvent';

test('decode erc20', () => {
    const transferEvent = AbiEvent.fromJSON({
        'name': 'Transfer',
        'type': 'event',
        'anonymous': false,
        'inputs': [
            {
                'indexed': true,
                'name': 'from',
                'type': 'address'
            },
            {
                'indexed': true,
                'name': 'to',
                'type': 'address'
            },
            {
                'indexed': false,
                'name': 'value',
                'type': 'uint256'
            }
        ]
    });

    const decoded = transferEvent.decode({
        'address': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        'topics': [
            '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef',
            '0x0000000000000000000000009866103b576bc362e934b8e96115e72413b6a8c2',
            '0x0000000000000000000000000000000000009cb77a0c864c0b1ca56062140580'
        ],
        'data': '0x00000000000000000000000000000000000000000000000001cc3fba27ab512a',
        'blockNumber': 14990200,
        'transactionHash': '0x85c731b7f3c4f987698871b0bf7f742015335a423bdc9471efcc4560806d39d9',
        'transactionIndex': 8,
        'blockHash': '0x4e4c22998b0d8b338e705100862e97208b7c10b669375eb53b35504ed4ee4ce2',
        'logIndex': 50,
        'removed': false
    });

    expect(decoded.get().toJson()).toEqual({
        'from': '0x9866103b576bc362e934b8e96115e72413b6a8c2',
        'to': '0x0000000000009cb77a0c864c0b1ca56062140580',
        'value': BigInt('129548558048907562')
    });
});

test('decode erc1155', () => {
    const transferEvent = AbiEvent.fromJSON({
        'anonymous': false,
        'inputs': [
            {
                'indexed': true,
                'internalType': 'address',
                'name': 'operator',
                'type': 'address'
            },
            {
                'indexed': true,
                'internalType': 'address',
                'name': 'from',
                'type': 'address'
            },
            {
                'indexed': true,
                'internalType': 'address',
                'name': 'to',
                'type': 'address'
            },
            {
                'indexed': false,
                'internalType': 'uint256[]',
                'name': 'ids',
                'type': 'uint256[]'
            },
            {
                'indexed': false,
                'internalType': 'uint256[]',
                'name': 'values',
                'type': 'uint256[]'
            }
        ],
        'name': 'TransferBatch',
        'type': 'event'
    });

    const decoded = transferEvent.decode({
        'address': '0x76be3b62873462d2142405439777e971754e8e77',
        'topics': [
            '0x4a39dc06d4c0dbc64b70af90fd698a233a518aa5d07e595d983b8c0526c8f7fb',
            '0x000000000000000000000000a148fccc6e42f127721a44ced43bf971adb15d6a',
            '0x0000000000000000000000004796d0940a89475d733e60098c2123e96f954355',
            '0x00000000000000000000000065b75b8a8b5053dbd2475e26aa1210dc39774ef5'
        ],
        'data': '0x00000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000220000000000000000000000000000000000000000000000000000000000000000e000000000000000000000000000000000000000000000000000000000000283a000000000000000000000000000000000000000000000000000000000000283b00000000000000000000000000000000000000000000000000000000000028660000000000000000000000000000000000000000000000000000000000002883000000000000000000000000000000000000000000000000000000000000292100000000000000000000000000000000000000000000000000000000000029c600000000000000000000000000000000000000000000000000000000000029ef0000000000000000000000000000000000000000000000000000000000002a010000000000000000000000000000000000000000000000000000000000002a250000000000000000000000000000000000000000000000000000000000002a2b0000000000000000000000000000000000000000000000000000000000002a440000000000000000000000000000000000000000000000000000000000002a5c0000000000000000000000000000000000000000000000000000000000002ace0000000000000000000000000000000000000000000000000000000000002b09000000000000000000000000000000000000000000000000000000000000000e00000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000003000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001',
        'blockNumber': '0x101a85a',
        'transactionHash': '0x758dd7bfc308a19e95b6167bfa2ce5e5362596f70e7db679e5719f5974aaa800',
        'transactionIndex': '0x4f',
        'blockHash': '0x7cb94e30af3ba689c9de3638a1ce4a782469ed63b83838db836b0ce0c46aa9f9',
        'logIndex': '0xc7',
        'removed': false
    });

    expect(decoded.get().toJson()).toEqual({
        'from': '0x4796d0940a89475d733e60098c2123e96f954355',
        'to': '0x65b75b8a8b5053dbd2475e26aa1210dc39774ef5',
        'operator': '0xa148fccc6e42f127721a44ced43bf971adb15d6a',
        'ids': [
            10298, 10299, 10342, 10371, 10529, 10694, 10735, 10753, 10789, 10795, 10820, 10844, 10958, 11017
        ].map(BigInt),
        'values': [
            1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1
        ].map(BigInt)
    });
});