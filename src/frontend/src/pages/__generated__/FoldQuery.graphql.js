/**
 * @flow
 */

/* eslint-disable */

'use strict';

/*::
import type { ConcreteRequest } from 'relay-runtime';
export type FoldQueryVariables = {||};
export type FoldQueryResponse = {|
  +observations: ?$ReadOnlyArray<?{|
    +id: string
  |}>
|};
export type FoldQuery = {|
  variables: FoldQueryVariables,
  response: FoldQueryResponse,
|};
*/


/*
query FoldQuery {
  observations {
    id
  }
}
*/

const node/*: ConcreteRequest*/ = (function(){
var v0 = [
  {
    "alias": null,
    "args": null,
    "concreteType": "ObservationsType",
    "kind": "LinkedField",
    "name": "observations",
    "plural": true,
    "selections": [
      {
        "alias": null,
        "args": null,
        "kind": "ScalarField",
        "name": "id",
        "storageKey": null
      }
    ],
    "storageKey": null
  }
];
return {
  "fragment": {
    "argumentDefinitions": [],
    "kind": "Fragment",
    "metadata": null,
    "name": "FoldQuery",
    "selections": (v0/*: any*/),
    "type": "Query",
    "abstractKey": null
  },
  "kind": "Request",
  "operation": {
    "argumentDefinitions": [],
    "kind": "Operation",
    "name": "FoldQuery",
    "selections": (v0/*: any*/)
  },
  "params": {
    "cacheID": "68b5860959ed488a94c19f3020fb9af7",
    "id": null,
    "metadata": {},
    "name": "FoldQuery",
    "operationKind": "query",
    "text": "query FoldQuery {\n  observations {\n    id\n  }\n}\n"
  }
};
})();
// prettier-ignore
(node/*: any*/).hash = '873cb55a415c553728f82a28df7867e7';

module.exports = node;
