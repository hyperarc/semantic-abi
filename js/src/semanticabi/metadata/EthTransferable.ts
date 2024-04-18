import {EthTransferType} from "semanticabi/metadata/EthTransferType";
import {Optional} from "common/Optional";

/**
 * Interface for things that can be transferred including root transaction, internal transaction, and token transfers.
 *
 * @author zuyezheng
 */
export interface EthTransferable {

    /**
     * Contract address for the transfer.
     */
    get contractAddress(): string;

    get fromAddress(): string;

    get toAddress(): string;

    get value(): Optional<number>;

    get transferType(): EthTransferType;

}