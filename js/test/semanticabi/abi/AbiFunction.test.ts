import {AbiFunction} from "semanticabi/abi/item/AbiFunction";

test('decode buyCover', () => {
    const buyCoverFunction = AbiFunction.fromJSON({
        'inputs': [
            {
                'components': [
                    {
                        'internalType': 'uint256',
                        'name': 'coverId',
                        'type': 'uint256'
                    },
                    {
                        'internalType': 'address',
                        'name': 'owner',
                        'type': 'address'
                    },
                    {
                        'internalType': 'uint24',
                        'name': 'productId',
                        'type': 'uint24'
                    },
                    {
                        'internalType': 'uint8',
                        'name': 'coverAsset',
                        'type': 'uint8'
                    },
                    {
                        'internalType': 'uint96',
                        'name': 'amount',
                        'type': 'uint96'
                    },
                    {
                        'internalType': 'uint32',
                        'name': 'period',
                        'type': 'uint32'
                    },
                    {
                        'internalType': 'uint256',
                        'name': 'maxPremiumInAsset',
                        'type': 'uint256'
                    },
                    {
                        'internalType': 'uint8',
                        'name': 'paymentAsset',
                        'type': 'uint8'
                    },
                    {
                        'internalType': 'uint16',
                        'name': 'commissionRatio',
                        'type': 'uint16'
                    },
                    {
                        'internalType': 'address',
                        'name': 'commissionDestination',
                        'type': 'address'
                    },
                    {
                        'internalType': 'string',
                        'name': 'ipfsData',
                        'type': 'string'
                    }
                ],
                'internalType': 'struct BuyCoverParams',
                'name': 'params',
                'type': 'tuple'
            },
            {
                'components': [
                    {
                        'internalType': 'uint40',
                        'name': 'poolId',
                        'type': 'uint40'
                    },
                    {
                        'internalType': 'bool',
                        'name': 'skip',
                        'type': 'bool'
                    },
                    {
                        'internalType': 'uint256',
                        'name': 'coverAmountInAsset',
                        'type': 'uint256'
                    }
                ],
                'internalType': 'struct PoolAllocationRequest[]',
                'name': 'poolAllocationRequests',
                'type': 'tuple[]'
            }
        ],
        'name': 'buyCover',
        'outputs': [
            {
                'internalType': 'uint256',
                'name': 'coverId',
                'type': 'uint256'
            }
        ],
        'stateMutability': 'payable',
        'type': 'function',
        'extra': {
            'provider': 'Nexus Mutual',
            'version': 'v2'
        }
    });

    const trace = {
        'action': {
            'from': '0x666b8ebfbf4d5f0ce56962a25635cff563f13161',
            'callType': 'call',
            'gas': '0xad003',
            'input': '0xf6579632000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000666b8ebfbf4d5f0ce56962a25635cff563f1316100000000000000000000000000000000000000000000000000000000000000560000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000004f68ca6d8cd91c6000000000000000000000000000000000000000000000000000000000000000278d0000000000000000000000000000000000000000000000000175a9793cd169c6f800000000000000000000000000000000000000000000000000000000000000ff00000000000000000000000000000000000000000000000000000000000005dc000000000000000000000000586b9b2f8010b284a0197f392156f1a7eb5e86e90000000000000000000000000000000000000000000000000000000000000160000000000000000000000000000000000000000000000000000000000000002e516d634236564e7572626f3553774736556751315053416435794b717736685052384543704a38384167336751610000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000b0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004f68cd29bf956be1bc6c',
            'to': '0xcafeac0ff5da0a2777d915531bfa6b29d282ee62',
            'value': '0x0'
        },
        'blockHash': '0x045f36375354439dce25dde47076224bb760a059cf1678394d8af4d15c5ce86f',
        'blockNumber': 17733888,
        'result': {
            'gasUsed': '0x59458',
            'output': '0x00000000000000000000000000000000000000000000000000000000000000ae'
        },
        'subtraces': 1,
        'traceAddress': [2, 0, 0],
        'transactionHash': '0x2ebe523aa93efb172caa55e3b1383786f800e769c546abf5104a9135944732b6',
        'transactionPosition': 91,
        'type': 'call'
    };

    const decoded = buyCoverFunction.decode(trace['action']['input']);

    expect(decoded.toJson()).toEqual({
        "params": {
            "amount": BigInt("375000000000000000000000"),
            "commissionDestination": "0x586b9b2f8010b284a0197f392156f1a7eb5e86e9",
            "commissionRatio": BigInt(1500),
            "coverAsset": BigInt(1),
            "coverId": BigInt(0),
            "ipfsData": "QmcB6VNurbo5SwG6UgQ1PSAd5yKqw6hPR8ECpJ88Ag3gQa",
            "maxPremiumInAsset": BigInt("26925185149329590008"),
            "owner": "0x666b8ebfbf4d5f0ce56962a25635cff563f13161",
            "paymentAsset": BigInt(255),
            "period": BigInt(2592000),
            "productId": BigInt(86)
        },
        "poolAllocationRequests": [
            {
                "coverAmountInAsset": BigInt("375000197088268066602092"),
                "poolId": BigInt(11),
                "skip": false
            }
        ]
    });
});
