import { aliasMutation, aliasQuery } from "../utils/graphql-test-utils";

describe("The Login Page", () => {
  beforeEach(() => {
    cy.intercept("http://localhost:8000/graphql/", (req) => {
      aliasMutation(req, "LoginMutation", "loginMutation.json");
      aliasQuery(req, "FoldQuery", "foldQuery.json");
      aliasQuery(req, "FoldTableRefetchQuery", "foldQuery.json");
      aliasQuery(req, "SearchQuery", "searchQuery.json");
    });
  });

  it("sets auth token when logging in via form submission", () => {
    cy.visit("/");
    cy.location("pathname").should("equal", "/login/");

    cy.get("input[name=username]").type("buffy@sunnydale.com");
    cy.get("input[name=password]").type("slayer!#1");
    cy.contains("button", "Sign in").click();

    cy.wait("@LoginMutation")
      .its("response.body.data.tokenAuth")
      .should("have.property", "token");

    cy.contains("Fold Observations").should("be.visible");
    cy.contains("Loading...").should("be.visible");

    cy.wait("@FoldQuery");

    cy.contains("Loading...").should("not.exist");
    cy.contains("Unique Pulsars").should("be.visible");
  });

  it("should redirect to login and back if not authenticated", () => {
    cy.visit("/search/");
    cy.location("pathname").should("equal", "/login/search");

    cy.get("input[name=username]").type("buffy@sunnydale.com");
    cy.get("input[name=password]").type("slayer!#1");
    cy.contains("button", "Sign in").click();

    cy.wait("@LoginMutation")
      .its("response.body.data.tokenAuth")
      .should("have.property", "token");

    cy.wait("@SearchQuery");

    cy.contains("Loading...").should("not.exist");
    cy.contains("Search mode Observations").should("be.visible");
    cy.contains("Pulsars").should("be.visible");

    cy.location("pathname").should("equal", "/search/");
  });
});
