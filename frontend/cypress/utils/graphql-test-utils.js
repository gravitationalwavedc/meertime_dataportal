// Utility to match GraphQL mutation based on the operation name
export const hasOperationName = (req, operationName) => {
  const { body } = req;
  return Object.hasOwn(body, "query") && body.query.includes(operationName);
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
