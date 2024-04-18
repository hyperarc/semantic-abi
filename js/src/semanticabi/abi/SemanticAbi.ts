import {ExpressionJson, Expressions} from "semanticabi/abi/item/semantic/Expressions";
import {EvmChain} from "semanticabi/metadata/EvmChain";
import {
    SemanticAbiValidateable,
    SemanticAbiValidationError
} from "semanticabi/abi/item/semantic/SemanticAbiValidateable";
import {Optional} from "common/Optional";
import {SemanticAbiFunction} from "semanticabi/abi/item/semantic/SemanticAbiFunction";
import {SemanticAbiEvent} from "semanticabi/abi/item/semantic/SemanticAbiEvent";
import {ItemType} from "semanticabi/abi/item/ItemType";
import {HexNormalize} from "semanticabi/transform/column/HexNormalize";
import Web3 from "web3";
import {SemanticAbiItem, SemanticAbiItemJson} from "semanticabi/abi/item/semantic/SemanticAbiItem";
import {Match} from "semanticabi/abi/item/semantic/Match";

export type SemanticAbiMetadataJson = {
    chains: string[],
    contractAddresses: string[],
    expressions?: ExpressionJson[]
}

export type SemanticAbiJson = {
    metadata: SemanticAbiMetadataJson
    abi: SemanticAbiItemJson[]
}

/**
 * The semantic ABI for a smart contract. This contains all the details needed to decode the logs and transforms them
 * into individual rows.
 */
export class SemanticAbi implements SemanticAbiValidateable {

    // Chains to run the semantic ABI for.
    public readonly chains: Set<EvmChain>;
    // Specific contract addresses to filter on.
    public readonly contractAddresses: Set<string>;
    // Table-level expressions to evaluate for each row.
    public readonly expressions: Expressions;

    // Parsed events and functions by type.
    public readonly events: Map<string, SemanticAbiEvent>;
    public readonly functions: Map<string, SemanticAbiFunction>;

    constructor(
        public readonly abiJson: SemanticAbiJson
    ) {
        this.chains = new Set(abiJson.metadata.chains.map(chain => EvmChain.get(chain)));
        this.contractAddresses = new Set(
            Optional.of(abiJson.metadata.contractAddresses)
                .map(addresses => addresses.map(HexNormalize.normalize))
                .getOr([])
        );

        // parse all the events and functions we'll need to decode
        this.events = new Map();
        this.functions = new Map();
        this.abiJson.abi.forEach(item => {
            const itemType = ItemType.get(item.type);
            if (itemType === ItemType.FUNCTION) {
                const functionItem = SemanticAbiFunction.fromJSON(item);
                this.functions.set(functionItem.rawItem.hash, functionItem);
            } else if (itemType === ItemType.EVENT) {
                const eventItem = SemanticAbiEvent.fromJSON(item);
                this.events.set(eventItem.rawItem.hash, eventItem);
            }
        });
    }

    eventBySignature(signature: string): Optional<SemanticAbiEvent> {
        return Optional.of(this.events.get(Web3.utils.soliditySha3(signature).slice(2)));
    }

    functionBySignature(signature: string): Optional<SemanticAbiFunction> {
        return Optional.of(this.functions.get(Web3.utils.soliditySha3(signature).slice(2, 10)));
    }

    validate(): Optional<SemanticAbiValidationError> {
        const validateMatch = (match: Match): Optional<SemanticAbiValidationError> => {
            return this.matchItem(match).match(
                // matched something, all good
                () => Optional.none(),
                // missing match
                () => SemanticAbiValidationError.some(`No match for signature ${match.signature}.`)
            );
        };

        let hasPrimary = false;
        for (const item of [...this.events.values(), ...this.functions.values()]) {
            hasPrimary = hasPrimary || item.properties.isPrimary;

            // validate the item
            const validation = item.validate()
                // and with respect to other items it might need
                .orElse(() => item.properties.matches.flatMap(
                    matches => matches.matches.reduce(
                        (acc, match) => acc.orElse(() => validateMatch(match)),
                        Optional.none<SemanticAbiValidationError>()
                    )
                ));
            if (validation.isPresent) {
                return validation;
            }
        }

        return Optional.bool(!hasPrimary)
            .map(() => new SemanticAbiValidationError('At least one primary ABI item must be specified.'));
    }

    /**
     * Find the matching item which only compares signatures.
     */
    matchItem(match: Match): Optional<SemanticAbiItem> {
        switch (match.type) {
            case ItemType.EVENT:
                return match.signature.flatMap(s => this.eventBySignature(s));
            case ItemType.FUNCTION:
                return match.signature.flatMap(s => this.functionBySignature(s));
            default:
                return Optional.none();
        }
    }

    shouldConsider(contractAddress: string): boolean {
        return this.contractAddresses.size === 0 || this.contractAddresses.has(contractAddress);
    }

}