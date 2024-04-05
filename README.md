# semantic-abi
A tool for converting the data in logs and function traces in a transaction for an ABI into a tabular format. This is accomplished by adding declarative semantics to the existing ABI through inline annotations added to the events and functions.

## Specification
A Semantic ABI is a JSON object that contains two parts, a metadata section and a list of events and functions from your ABI.
```json
{
    "metadata": {
        // Basic naming metadata, doesn't affect parsing in any way
        "name": "My ABI",
        "project": "My Project",
        "version": "v2",
        // A list of contract addresses to filter on along with topic filtering in
        // case the topic for the primary ABIs is fairly generic and common
        "contractAddresses": [],
        // List of chains that we will inspect blocks from to find transactions
        "chains": ["optimism"],
        // A list of expressions to apply to each row after all item-level
        // transforms have been applied
        "expressions": [
            {
                "name": "blah",
                "expression": "'blah'",
                "type": "string"
            }
        ]
    },
    "abi": [
        ...
    ]
}
```
The only required field in the `metadata` section is `chains`, and the valid values for that can be found in `python/semanticabi/metadata/EvmChain.py`. The `contractAddresses` field is optional and is used to filter out logs that don't match the contract address. The `expressions` field is optional and is used to apply an expression to each row after all item-level transforms have been applied (expressions will be explained later).

### Item-level annotations
The `abi` section is a list of events and functions from your ABI, as defined by the [Ethereum ABI Specification](https://docs.soliditylang.org/en/latest/abi-spec.html#json). In each of these items, the following annotations can be applied:
* `@isPrimary` - When this is set to `true`, this event or function will be used to generate a row for each log or trace of that event or function in a transaction. By default, each row will contain a column for every non-array input and output parameter in the item. For tuple parameters, the component parameters will be recursively included in the row, with a name of `<tuple name>_<component name>` This is required for at least one event or function in the ABI.
  ```json
  {
      "@isPrimary": true,
      "name": "Transfer",
      "type": "event",
      "inputs": [
          {
              "name": "from",
              "type": "address",
              "indexed": true
          }
      ]
  }
  ```
* `@explode` - This is an object containing a field `paths`, which is an array of dotted paths of parameters in the ABI item to array parameters that should be "exploded" into one row per value in the array. Multiple paths to different arrays can be specified as long as the arrays are all the same length, and then for each index across all the arrays, the values at that index will be used to generate a single row. To specify an array parameter nested within a tuple, use a dot `.` to combine the tuple's name with the name of the array parameter. Only primary items may have an `explode`. The exploded parameters will be added to the output after all the default parameters for a primary abi have been added to the output.
  ```json
  {
      "@isPrimary": true,
      "@explode": {
          "paths": [
              "amounts",
              "to.address"
          ]
      },
      "name": "Transfer",
      "type": "event",
      "inputs": [
          {
              "name": "from",
              "type": "address",
              "indexed": true
          },
          {
              "name": "amounts",
              "type": "uint256[]",
              "indexed": false
          },
          {
              "name": "to",
              "type": "tuple",
              "indexed": true,
              "components": [
                  {
                      "name": "address",
                      "type": "address[]"
                  }
              ]
          }
      ]
  }
  ```
  * [Example contract](./python/test/resources/contracts/seaport/abis/explode/multiple.json) - [Output](/python/test/abi/steps/test_ExplodeStep.py#L25)
* `@matches` - Matches are used to "join" another item's data to this item, and multiple items can be matched in order. Only primary items may contain a match. The columns from the matched item(s) will be added to the output after any exploded parameters have been added.
  ```json
  [
      {
          "name": "EventA",
          "type": "event",
          "inputs": [
              {
                  "name": "from",
                  "type": "address",
                  "indexed": true
              },
              {
                  "name": "value",
                  "type": "uint256",
                  "indexed": true
              }
          ]
      },
      {
          "@isPrimary": true,
          "@matches": [
              {
                  "signature": "EventA(address,value)",
                  "type": "event",
                  "prefix": "EventA",
                  "assert": "onlyOne",
                  "predicates": [
                      {
                          "type": "equal",
                          "source": "from",
                          "matched": "from"
                      }
                  ]
              }
          ],
          "name": "EventB",
          "type": "event",
          "inputs": [
              {
                  "name": "from",
                  "type": "address",
                  "indexed": true
              },
              {
                  "name": "to",
                  "type": "address",
                  "indexed": true
              }
          ]
      }
  ]
  ```
  A match contains a few parts:
  * `signature` - The ABI signature of the item being matched, for example `Transfer(address,address,uint256)`. This is required, unless the type is `transfer`.
  * `type` - The type of item being matched, either `event` or `function`. There is also a third "special" type, `transfer` that matches against any of the various transfer events. A transfer contains fields of `fromAddress`, `toAddress`, `value`, `tokenId`, and `tokenType`. This is required.
    * [Example contract matching a function](./python/test/resources/contracts/seaport/abis/match/function_onlyone.json)
    * [Example contract matching an event](./python/test/resources/contracts/seaport/abis/match/event_onlyone.json)
    * [Example contract matching a transfer](./python/test/resources/contracts/seaport/abis/match/event_multiple_with_transfer.json)
  * `prefix` - A string that will be prepended to the field names of the matched item. If there are multiple matches against an item of the same signature, they must all have unique prefixes. This is required
  * `assert` - An assertion to make after applying the match predicates. Possible values are:
    * `onlyOne` - Assert that exactly one match is found
    * `many` - Assert that at least one match is found. One row will be generated for each matched item. This cannot be used in combination with an `@explode` on the same item
    * `optionalOne` - Assert that at most one match is found
  * `predicates` - A list of predicates used to determine if an item of the specified type and signature should be matched. The following predicate types are available:
    * `equal` - The value in the `source` column must be equal to the value in the `matched` column
      ```json
      {
        "type": "equal",
        "source": "from",
        "matched": "from"
      }
      ```
    * `in` - The value in the `source` column must be in one of the values in the `matched` columns
      ```json
      {
        "type": "in",
        "source": "address",
        "matched": ["from", "to"]
      }
      ```
    * `bound` - The value in the `source` column must be within the bounds of `matched` columns. The bounds can be specified with `lower` or `upper` (or both), which are specified as a percent of the `source` value, where "1" equals 100%
      * If `lower` is specified, then `matched` >= `lower` * `source`
      * If `upper` is specified, then `matched` <= `upper` * `source`
      ```json
      {
        "type": "bound",
        "source": "value",
        "matched": "value",
        "lower": 0.9,
        "upper": 1.1
      }
      ```
* `@expressions` - Expressions are used to add new columns (or modify existing columns) in the output. This is an array of objects, each containing a `name`, `expression`, and `type`. The `name` is the name of the column, the `expression` is a basic mathematical expression with operators `+`, `-`, `*`, `/`, and `**` (exponent), or a string expression using the `||` to concatenate two strings, and the `type` is the output type of the column (one of `int`, `double`, or `string`). The expression can also reference any column in the row, and the result of the expression will be added as a new column in the output (or overwrite an existing column). These expressions will be applied after any matched item columns have been added to the output. This is optional.
  ```json
  {
      "@isPrimary": true,
      "@expressions": [
          {
              "name": "myNewColumn",
              "expression": "value * 2",
              "type": "int"
          }
      ],
      "name": "Transfer",
      "type": "event",
      "inputs": [
          {
              "name": "from",
              "type": "address",
              "indexed": true
          },
          {
              "name": "value",
              "type": "uint256",
              "indexed": true
          }
      ]
  }
  ```
  * [Example contract](./python/test/resources/contracts/seaport/abis/expressions/expressions.json) - [Output](./python/test/abi/steps/test_ExpressionListStep.py#L21)
  * The `expressions` field in the `metadata` section follows these same rules, and is applied after all item-level transforms have been applied

### Parameter-level annotations
In addition to the item-level annotations, there are also parameter-level annotations that can be applied to the individual parameters in the `inputs` and `outputs` of an ABI item. These annotations are applied as keys in the parameter object, and are as follows:

* `@exclude` - By default, all non-array parameters are included in the output. If you want to exclude a parameter from the output, you can set this to `true`. This is optional.
  ```json
  {
      "name": "from",
      "type": "address",
      "indexed": true,
      "@exclude": true
  }
  ```
* `@transform` - This applies some basic transformations to a parameter. All of these transforms are optional
  * `name` - Renames the column in the output to this value
  * `type` - Changes the type of the column in the output to this value. The valid values are `int`, `double`, and `string`
  * `expression` - An expression that follows the same rules as the `@expressions` annotation, but the only column it can reference is itself, via the name `this`
  ```json
  {
      "name": "value",
      "type": "uint256",
      "indexed": true,
      "@transform": {
          "name": "newValue",
          "type": "string",
          "expression": "this * 2"
      }
  }
  ```
