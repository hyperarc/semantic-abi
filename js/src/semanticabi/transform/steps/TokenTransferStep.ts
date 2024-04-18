import {Step} from "semanticabi/transform/steps/Step";
import {AbiSchema} from "semanticabi/transform/steps/AbiSchema";
import {DataType} from "semanticabi/transform/column/DataType";
import {TokenTransferDecoded} from "semanticabi/metadata/TokenTransferDecoded";
import {TransformItem} from "semanticabi/transform/steps/TransformItem";
import {EthBlock} from "semanticabi/metadata/EthBlock";
import {EthTransaction} from "semanticabi/metadata/EthTransaction";
import {JsonObject} from "common/CommonTypes";
import { SemanticAbiItem } from "semanticabi/abi/item/semantic/SemanticAbiItem";
import { SemanticAbi } from "semanticabi/abi/SemanticAbi";

const SCHEMA: AbiSchema = new AbiSchema([
    DataType.hashColumn('fromAddress'),
    DataType.hashColumn('toAddress'),
    DataType.NUMBER.column('value'),
    DataType.STRING.column('tokenId'),
    DataType.STRING.column('tokenType')
]);

/**
 * Special step to handle token transfer matches. This takes all the various transfer events from the transaction and
 * generates a single row for each transfer event, with the from, to, value, tokenId, and tokenType fields.
 */
export class TokenTransferStep extends Step {

    get abi(): SemanticAbi {
        throw new Error("Method not implemented.");
    }

    get abiItem(): SemanticAbiItem {
        throw new Error("Method not implemented.");
    }

    get shouldTransform(): boolean {
        throw new Error("Method not implemented.");
    }

    get schema(): AbiSchema {
        return SCHEMA;
    }

    innerTransform(block: EthBlock, transaction: EthTransaction): [TransformItem, JsonObject[]][] {
        return transaction.transfers.map(transfer =>
            [
                new TokenTransferTransformItem(transfer),
                [{
                    'fromAddress': transfer.fromAddress,
                    'toAddress': transfer.toAddress,
                    'value': transfer.value.nullable,
                    'tokenId': transfer.tokenId.map(id => id.toString()).nullable,
                    'tokenType': transfer.tokenType.name
                }]
            ]
        );
    }

}

class TokenTransferTransformItem extends TransformItem {

    constructor(
        private readonly tokenTransfer: TokenTransferDecoded
    ) {
        super(() => null);
    }

    get contractAddress(): string {
        return this.tokenTransfer.contractAddress;
    }

    get internalIndex(): string {
        return this.tokenTransfer.internalIndex.toString();
    }

    get itemType(): string {
        return 'transfer';
    }

}
