import { Environment, Network, RecordSource, Store } from "relay-runtime";

const HTTP_ENDPOINT = import.meta.env.VITE_GRAPHQL_API;

const fetchFn = async (request, variables) => {
  const token = localStorage.getItem("jwt");

  const resp = await fetch(HTTP_ENDPOINT, {
    method: "POST",
    headers: {
      Accept:
        "application/graphql-response+json; charset=utf-8, application/json; charset=utf-8",
      "Content-Type": "application/json",
      // <-- Additional headers like 'Authorization' would go here
      Authorization: `JWT ${token}`,
    },
    body: JSON.stringify({
      query: request.text, // <-- The GraphQL document composed by Relay
      variables,
    }),
  });

  return await resp.json();
};

function createRelayEnvironment() {
  return new Environment({
    network: Network.create(fetchFn),
    store: new Store(new RecordSource()),
  });
}

const environment = createRelayEnvironment();

export default environment;
