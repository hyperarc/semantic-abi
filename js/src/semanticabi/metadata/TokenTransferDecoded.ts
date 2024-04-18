import {EthTransferable} from "semanticabi/metadata/EthTransferable";
import {EthLog} from "semanticabi/metadata/EthLog";
import {JsonObject} from "common/CommonTypes";
import {Optional} from "common/Optional";
import {EthTransferType} from "semanticabi/metadata/EthTransferType";
import {EthTokenType} from "semanticabi/metadata/EthTokenType";
import {DecodedLog} from "semanticabi/abi/decoded/DecodedLog";
import {Abi} from "semanticabi/abi/Abi";

/**
 * Handles the edge cases of decoding transfers for Erc20, Erc721, and Erc1155.
 *
 * @author zuyezheng
 */
export class TokenTransferDecoded implements EthTransferable {

    // signatures that match token transfers
    static readonly SIGNATURES = new Set([
        //Transfer(address,address,uint256)
        '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef',
        // TransferSingle(address,address,address,uint256,uint256)
        '0xc3d58168c5ae7397731d063d5bbf3d657854427343f4c083240f7aacaa2d0f62',
        // TransferBatch(address,address,address,uint256[],uint256[])
        '0x4a39dc06d4c0dbc64b70af90fd698a233a518aa5d07e595d983b8c0526c8f7fb',

        // Depending on if it's a transfer or purchase, only one of these will be emitted (most of the times)
        // PunkTransfer(address,address,uint256)
        '0x05af636b70da6819000c49f85b21fa82081c632069bb626f30932034099107d8',
        // PunkBought(uint256,uint256,address,address)
        '0x58e5d5a525e3b40bc15abaa38b5882678db1ee68befd2f60bafe3a7fd06db9e3'
    ]);

    public readonly value: Optional<number>;

    constructor(
        public readonly log: EthLog,
        public readonly decoded: JsonObject,
        public readonly fromAddress: string,
        public readonly toAddress: string,
        value: number,
        public readonly tokenId: Optional<number>,
        public readonly eventName: EventName,
        public readonly tokenType: EthTokenType,
        public readonly internalIndex: string
    ) {
        this.value = Optional.some(value);
    }

    get contractAddress(): string {
        return this.log['address'].toLowerCase();
    }

    get transferType(): EthTransferType {
        return EthTransferType.ERC;
    }

    /**
     * Operator field specific to 1155.
     */
    get operator(): string {
        return this.decoded['operator'].toLowerCase();
    }

    /**
     * Attempt to decode and return any transfers. This will silently skip any errors.
     */
    static tryDecode(abi: Abi, log: EthLog, logI: number): TokenTransferDecoded[] {
        if (!TokenTransferDecoded.isA(log)) {
            return [];
        }

        try {
            return abi.decodeLog(log)
                .map(decoded => TokenTransferDecoded.of(log, logI, decoded))
                .getOr([]);
        } catch (e) {
            // silently skip
        }

        return [];
    }

    /**
     * If the log is a support transfer.
     */
    static isA(log: EthLog): boolean {
        return Optional.of(log['topics'])
            .map(topics => topics[0])
            .map(topic => this.SIGNATURES.has(topic))
            .getOr(false);
    }

    /**
     * Factory given decoded log, returning 0 or more token transfers.
     */
    static of(log: EthLog, logI: number, decodedLog: DecodedLog): TokenTransferDecoded[] {
        const decoded = decodedLog.data.toJson();
        const eventName = decodedLog.event.name as EventName;

        const make = (
            value: number, tokenId: Optional<number>, tokenType: EthTokenType, internalIndex: string = logI.toString()
        ): TokenTransferDecoded => {
            return new TokenTransferDecoded(
                log,
                decoded,
                decoded['from'],
                decoded['to'],
                value,
                tokenId,
                eventName,
                tokenType,
                internalIndex
            );
        };

        switch (decodedLog.event.name) {
            case 'Transfer':
                return decodedLog.event.extra['standard'] === 'Erc721' ?
                    [make(1, Optional.some(decoded['tokenId']), EthTokenType.ERC721)] :
                    [make(decoded['value'], Optional.none(), EthTokenType.ERC20)];
            case 'TransferSingle':
                return [make(decoded['value'], Optional.of(decoded['id']), EthTokenType.ERC1155)];
            case 'TransferBatch':
                const padding: number = Math.floor(Math.log10(decoded['ids'].length)) + 1;
                const makeIndex = (i: number) => {
                    return logI.toString() + '.' +  (i + 1).toString().padStart(padding, '0');
                };

                return decoded['ids'].map(
                    (id: number, i: number) => make(
                        decoded['values'][i], Optional.some(id), EthTokenType.ERC1155, makeIndex(i)
                    )
                );
            case 'PunkTransfer':
                return [make(1, Optional.some(decoded['punkIndex']), EthTokenType.CRYPTO_PUNKS)];
            case 'PunkBought':
                return [new TokenTransferDecoded(
                    log,
                    decoded,
                    decoded['fromAddress'].toLowerCase(),
                    decoded['toAddress'].toLowerCase(),
                    1,
                    Optional.some(decoded['punkIndex']),
                    eventName,
                    EthTokenType.CRYPTO_PUNKS,
                    logI.toString()
                )];

        }
    }

}

export type EventName = 'Transfer' | 'TransferSingle' | 'TransferBatch' | 'PunkTransfer' | 'PunkBought';