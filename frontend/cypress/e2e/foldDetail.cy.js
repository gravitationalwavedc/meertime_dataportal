import { aliasMutation, aliasQuery } from "../utils/graphql-test-utils";

describe("The Fold Detail Page", () => {
  beforeEach(() => {
    cy.intercept("http://localhost:8000/graphql/", (req) => {
      aliasMutation(req, "LoginMutation", "loginMutation.json");
      aliasQuery(req, "FoldDetailQuery", "foldDetailQuery.json");
    });
    cy.visit("fold/meertime/J0125-2327/");
    cy.location("pathname").should("equal", "/login");

    cy.get("input[name=username]").type("buffy@sunnydale.com");
    cy.get("input[name=password]").type("slayer!#1");
    cy.contains("button", "Sign in").click();

    cy.wait("@LoginMutation")
      .its("response.body.data.tokenAuth")
      .should("have.property", "token");
  });

  it("displays loading then the data", () => {
    cy.contains("J0125-2327").should("be.visible");
    cy.contains("Loading...").should("be.visible");

    cy.wait("@FoldDetailQuery");

    cy.contains("Loading...").should("not.exist");
    cy.contains("PSR J0125-2327 is a millisecond pulsar").should("be.visible");
  });

  it("should toggle the ephemeris modal", () => {
    cy.wait("@FoldDetailQuery");
    cy.contains("View folding ephemeris").should("be.visible");
    cy.contains("Folding Ephemeris").should('not.exist')
    cy.contains("View folding ephemeris").click();
    cy.contains("Folding Ephemeris").should('be.visible')
  });

  it("should disable the view ephemeris button if the data is missing", () => {
    cy.intercept("http://localhost:8000/graphql/", (req) => {
      aliasQuery(req, "FoldDetailQuery", "foldDetailQueryNoEphem.json");
    });
    cy.wait("@FoldDetailQuery");
    cy.contains("Folding ephemeris unavailable").should("be.visible");
  });
});
