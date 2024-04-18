import {AbiItem, AbiItemJson} from "semanticabi/abi/item/AbiItem";
import {Parameters} from "semanticabi/abi/item/Parameters";
import {DecodedTuple} from "semanticabi/abi/decoded/DecodedTuple";
import {JsonObject} from "common/CommonTypes";
import Web3 from "web3";
import {Optional} from "common/Optional";
import {EthLog} from "semanticabi/metadata/EthLog";

/**
 * Parse out a function definition and encapsulate it for decoding.
 *
 * @author zuyezheng
 */
export class AbiEvent extends AbiItem {

    public readonly hash: string;
    public readonly numIndexed: number;

    static fromJSON(itemJson: AbiItemJson): AbiEvent {
        return new AbiEvent(
            itemJson['name'],
            Parameters.fromJSON(itemJson['inputs']),
            itemJson['extra']
        );
    }

    constructor(
        name: string,
        inputs: Parameters,
        extra: JsonObject
    ) {
        super(name, inputs, extra);

        this.hash = Web3.utils.soliditySha3(this.signature).slice(2);
        this.numIndexed = inputs.parameters(true).length;
    }

    isOf(log: JsonObject): boolean {
        // make sure there are topics
        const topics: string[] = log['topics'];
        if (topics.length === 0) {
            return false;
        }

        // check signature
        if (topics[0].slice(2) !== this.hash) {
            return false;
        }

        // check number of expected indexed parameters since indexed-ness is not accounted for in the signature hash
        return this.numIndexed === topics.length - 1;
    }

    decode(input: EthLog): Optional<DecodedTuple> {
        // we'll be decoding out of order due to indexed vs unindexed parameters, map them so we can reorder at the end
        const decoded: JsonObject = {};

        // need topics, otherwise we can't decode
        if (!input['topics'] || input['topics'].length === 0) {
            return Optional.none();
        }

        // start with the indexed data first stored in topics, skip the first topic since it's the event hash and strip
        // leading 0x from each
        const topics: string[] = input['topics'];
        const indexedData = topics.slice(1).map(s => s.substring(2)).join('');
        const decodedValues = AbiItem.WEB3.eth.abi.decodeParameters(this.inputs.signatures(true), indexedData);
        this.inputs.parameters(true).forEach((parameter, i) => {
            decoded[parameter.name] = decodedValues[i];
        });

        const unindexedData = input['data'].slice(2);
        const unindexedDecodedValues = AbiItem.WEB3.eth.abi.decodeParameters(this.inputs.signatures(false), unindexedData);
        this.inputs.parameters(false).forEach((parameter, i) => {
            decoded[parameter.name] = unindexedDecodedValues[i];
        });

        return Optional.some(
            DecodedTuple.fromParametersAndValues(
                Optional.none(),
                this.inputs.parameters(),
                // reorder decoded values to match the signature
                this.inputs.parameters().map(p => decoded[p.name])
            )
        );
    }

}
