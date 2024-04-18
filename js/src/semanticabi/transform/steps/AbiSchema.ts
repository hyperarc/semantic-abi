import {DatasetColumn} from "semanticabi/transform/column/DatasetColumn";
import {OrderedMap} from "common/OrderedMap";
import {Optional} from "common/Optional";
import {SemanticAbiExecutionError} from "semanticabi/abi/item/semantic/SemanticAbiExecutionError";

/**
 * @author zuyezheng
 */
export class AbiSchema {

    private readonly _columns: OrderedMap<string, DatasetColumn>;

    constructor(columns: DatasetColumn[]) {
        this._columns = OrderedMap.fromKeyed(columns, c => c.name);
    }

    get columns(): DatasetColumn[] {
        return this._columns.values;
    }

    column(name: string): Optional<DatasetColumn> {
        return this._columns.get(name);
    }

    hasColumn(name: string): boolean {
        return this._columns.has(name);
    }

    /**
     * Append the list of columns to the existing columns.
     */
    withColumns(columns: DatasetColumn[], allowDupes: boolean = false): AbiSchema {
        if (allowDupes) {
            // make sure if the column is a dupe, it is of the same type
            Optional.of(columns.find(c =>
                // see if the column exists
                this._columns.get(c.name)
                    // if it does, return the column if there is a type mismatch so we can throw with it
                    .map(existingC => c.dataType !== existingC.dataType)
                    // all good
                    .getOr(false)
            )).forEach(c => {
                throw new SemanticAbiExecutionError(`Column with name '${c.name}' already exists and is a different type.`);
            });
        } else {
            // strictly check for dupes
            Optional.of(columns.find(c => this.hasColumn(c.name)))
                .forEach(c => {
                    throw new SemanticAbiExecutionError(`Column with name '${c.name}' already exists.`);
                });
        }

        return new AbiSchema(this.columns.concat(columns));
    }

    /**
     * Merge 2 schemas without allowing for duplicate column names, returning a new merged.
     */
    mergeSchema(other: AbiSchema, rename: (name: string) => string, allowDupes: boolean = false): AbiSchema {
        return this.withColumns(other.columns.map(c => c.withName(rename(c.name))), allowDupes);
    }

}