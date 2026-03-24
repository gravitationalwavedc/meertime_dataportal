// Utility to match GraphQL mutation based on the operation name
export const hasOperationName = (req, operationName) => {
  const { body } = req;
  return Object.hasOwn(body, "query") && body.query.includes(operationName);
};

const getVariables = (req) => {
  if (!req.body || typeof req.body !== "object") {
    return {};
  }
  return req.body.variables && typeof req.body.variables === "object"
    ? req.body.variables
    : {};
};

const valueDescription = (value) =>
  value === undefined ? "undefined" : JSON.stringify(value);

export const assertNoAllValues = (req, keys, operationName) => {
  const variables = getVariables(req);

  keys.forEach((key) => {
    if (variables[key] === "All") {
      throw new Error(
        `[GraphQL guardrail] ${operationName} sent forbidden "All" for "${key}". Variables: ${JSON.stringify(
          variables
        )}`
      );
    }
  });
};

export const assertEmptyStringOrConcrete = (req, keys, operationName) => {
  const variables = getVariables(req);

  keys.forEach((key) => {
    const value = variables[key];
    const isValid =
      typeof value === "string" && (value === "" || value.trim().length > 0);

    if (!isValid || value === "All") {
      throw new Error(
        `[GraphQL guardrail] ${operationName} expected "${key}" to be "" or a concrete string, got ${valueDescription(
          value
        )}. Variables: ${JSON.stringify(variables)}`
      );
    }
  });
};

// Alias query if operationName matches
export const aliasQuery = (req, operationName, fixture) => {
  if (hasOperationName(req, operationName)) {
    req.alias = operationName;
    req.reply({
      fixture: fixture,
    });
  }
};

// Alias mutation if operationName matches
export const aliasMutation = (req, operationName, fixture) => {
  if (hasOperationName(req, operationName)) {
    req.alias = operationName;
    req.reply({
      fixture: fixture,
    });
  }
};
