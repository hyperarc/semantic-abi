import {AbiEvent} from "semanticabi/abi/item/AbiEvent";
import {AbiFunction} from "semanticabi/abi/item/AbiFunction";
import {DecodedLog} from "semanticabi/abi/decoded/DecodedLog";
import {Optional} from "common/Optional";
import {DecodedTrace} from "semanticabi/abi/decoded/DecodedTrace";
import {EthTrace} from "semanticabi/metadata/EthTrace";
import {EthLog} from "semanticabi/metadata/EthLog";
import {AbiItemJson} from "semanticabi/abi/item/AbiItem";

/**
 * Parse an ABI and make it ready for decoding.
 *
 * @author
 */
export class Abi {

    // name of the ABI if we need to identify it later
    name: string;
    abi: AbiItemJson[];

    // events by hash, need to handle case of event hash collision due to order of indexed and unindexed parameters
    events: Map<string, AbiEvent[]>;
    // functions by hash, no need to worry about collisions
    functions: Map<string, AbiFunction>;

    constructor(name: string, abi: AbiItemJson[]) {
        this.name = name;
        this.abi = abi;
        this.events = new Map();
        this.functions = new Map();

        this.abi.forEach(item => {
            if (item.type === 'event') {
                const event = AbiEvent.fromJSON(item);
                if (!this.events.has(event.hash)) {
                    this.events.set(event.hash, []);
                }
                this.events.get(event.hash).push(event);
            } else if (item.type === 'function') {
                const functionItem = AbiFunction.fromJSON(item);
                this.functions.set(functionItem.hash, functionItem);
            }
        });
    }

    functionByName(name: string): AbiFunction | null {
        for (const fn of Object.values(this.functions)) {
            if (fn.name === name) {
                return fn;
            }
        }
        return null;
    }

    decodeLog(log: EthLog): Optional<DecodedLog> {
        if (log.topics.length === 0) {
            return Optional.none();
        }

        // first topic is always the signature hash
        const eventSignatureHash = log.topics[0].slice(2);

        // find any events with the signature
        return Optional.of(this.events.get(eventSignatureHash))
            // if more than 1 event, find the one that matches the expected number of indexed parameters
            .flatMap(events => events.length === 1 ? events[0] : events.find(e => e.isOf(log)))
            // do some decoding
            .flatMap(event => event.decode(log).map(decoded => new DecodedLog(event, decoded)));
    }

    decodeTrace(trace: EthTrace): Optional<DecodedTrace> {
        // find a matching signature
        return Optional.of(this.functions.get(trace.signature.map(s => s.slice(2)).nullable))
            // do some decoding if there is one
            .flatMap(fn => new DecodedTrace(
                fn,
                trace.input.map(i => fn.decode(i)),
                trace.output.filter(o => o.length > 2).map(o => fn.decodeOutput(o))
            ));
    }

}