import { aliasMutation, aliasQuery } from "../utils/graphql-test-utils";

describe("The Search Page", () => {
  beforeEach(() => {
    cy.intercept("http://localhost:8000/graphql/", (req) => {
      aliasMutation(req, "LoginMutation", "loginMutation.json");
      aliasQuery(req, "SearchQuery", "searchQuery.json");
    });
    cy.visit("/search/");
    cy.location("pathname").should("equal", "/login");

    cy.get("input[name=username]").type("buffy@sunnydale.com");
    cy.get("input[name=password]").type("slayer!#1");
    cy.contains("button", "Sign in").click();

    cy.wait("@LoginMutation")
      .its("response.body.data.tokenAuth")
      .should("have.property", "token");
  });

  it("displays loading then the data", () => {
    cy.contains("Search Mode Observations").should("be.visible");
    cy.contains("Loading...").should("be.visible");

    cy.wait("@SearchQuery");

    cy.contains("Loading...").should("not.exist");
    cy.contains("Pulsars").should("be.visible");
    cy.location("pathname").should("equal", "/search/");
  });
});
