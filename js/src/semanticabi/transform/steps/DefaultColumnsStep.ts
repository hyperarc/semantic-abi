import {SubsequentStep} from "semanticabi/transform/steps/SubsequentStep";
import {DatasetColumn} from "semanticabi/transform/column/DatasetColumn";
import { DataType } from "semanticabi/transform/column/DataType";
import {EthTransaction} from "semanticabi/metadata/EthTransaction";
import {EthBlock} from "semanticabi/metadata/EthBlock";
import { TransformItem } from "semanticabi/transform/steps/TransformItem";
import {HexNormalize} from "semanticabi/transform/column/HexNormalize";
import {HexToNumber} from "semanticabi/transform/column/HexToNumber";
import {Step} from "semanticabi/transform/steps/Step";
import {AbiSchema} from "semanticabi/transform/steps/AbiSchema";
import { JsonObject } from "common/CommonTypes";

const DEFAULT_COLUMNS: [DatasetColumn, (block: EthBlock, transaction: EthTransaction, item: TransformItem) => any][] = [
    [
        DataType.STRING.column('chain'),
        (block: EthBlock, transaction: EthTransaction, item: TransformItem) => block.chain.name
    ], [
        DataType.STRING.column('blockHash'),
        (block: EthBlock, transaction: EthTransaction, item: TransformItem) => HexNormalize.normalize(block.block['hash'])
    ], [
        DataType.NUMBER.column('blockNumber'),
        (block: EthBlock, transaction: EthTransaction, item: TransformItem) => HexToNumber.convert(block.number)
    ], [
        DataType.NUMBER.column('blockTimestamp'),
        (block: EthBlock, transaction: EthTransaction, item: TransformItem) => HexToNumber.convert(block.timestamp)
    ], [
        DataType.NUMBER.column('transactionHash'),
        (block: EthBlock, transaction: EthTransaction, item: TransformItem) => HexNormalize.normalize(transaction.hash)
    ], [
        DataType.STRING.column('transactionFrom'),
        (block: EthBlock, transaction: EthTransaction, item: TransformItem) => HexNormalize.normalize(transaction.fromAddress)
    ], [
        DataType.STRING.column('transactionTo'),
        (block: EthBlock, transaction: EthTransaction, item: TransformItem) => HexNormalize.normalize(transaction.toAddress)
    ], [
        DataType.STRING.column('contractAddress'),
        (block: EthBlock, transaction: EthTransaction, item: TransformItem) => HexNormalize.normalize(item.contractAddress)
    ], [
        DataType.NUMBER.column('status'),
        (block: EthBlock, transaction: EthTransaction, item: TransformItem) => HexToNumber.convert(transaction.receipt['status'])
    ], [
        DataType.NUMBER.column('gasUsed'),
        (block: EthBlock, transaction: EthTransaction, item: TransformItem) => HexToNumber.convert(transaction.receipt['gasUsed'])
    ], [
        DataType.STRING.column('itemType'),
        (block: EthBlock, transaction: EthTransaction, item: TransformItem) => item.itemType
    ], [
        DataType.STRING.column('internalIndex'),
        (block: EthBlock, transaction: EthTransaction, item: TransformItem) => item.internalIndex
    ]
];

/**
 * Adds a set of default columns to the output.
 */
export class DefaultColumnsStep extends SubsequentStep {

    public readonly schema: AbiSchema;

    constructor(previousStep: Step) {
        super(previousStep);
        this.schema = this.previousStep.schema.withColumns(DEFAULT_COLUMNS.map(([c, _]) => c));
    }

    protected innerTransformItem(
        block: EthBlock,
        transaction: EthTransaction,
        item: TransformItem,
        previousData: JsonObject[]
    ): JsonObject[] {
        return previousData.map(row => {
            for (const [column, valueFn] of DEFAULT_COLUMNS) {
                row[column.name] = valueFn(block, transaction, item);
            }
            return row;
        });
    }

}