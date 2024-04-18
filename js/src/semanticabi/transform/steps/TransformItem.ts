import {DecodedResult} from "semanticabi/abi/item/semantic/SemanticAbiItem";
import {Optional} from "common/Optional";

/**
 * Normalized wrapper for the event or function that is generating the associated rows in the output.
 */
export abstract class TransformItem {

    private readonly transformErrors: string[];
    private _decodedResult: DecodedResult;

    constructor(
        private readonly decodeResultFn: () => DecodedResult
    ) {
        this.transformErrors = [];
    }

    /**
     * The contract address that was interacted with to generate this item.
     */
    abstract get contractAddress(): string;

    /**
     * An index that uniquely identifies this item within the transaction.
     */
    abstract get internalIndex(): string;

    /**
     * The type of item this is, either 'event' or 'function', to help in uniquely identifying the item within the
     * transaction in combination with the internal index.
     */
    abstract get itemType(): string;

    /**
     * Lazily decode the result in case we filter out the item by contract address.
     */
    get decodedResult(): DecodedResult {
        if (!this._decodedResult) {
            this._decodedResult = this.decodeResultFn();
        }
        return this._decodedResult;
    }

    /**
     * Adds an error to the list of transform errors that will be reported at the end.
     */
    addTransformError(error: string): void {
        console.log(error);
        this.transformErrors.push(error);
    }

    /**
     * Returns true if there are any transform errors.
     */
    get hasTransformError(): boolean {
        return this.transformErrors.length > 0;
    }

    get transformError(): Optional<string> {
        return this.transformErrors.length > 0 ?
            Optional.some(this.transformErrors.join(', ')) :
            Optional.none();
    }

}