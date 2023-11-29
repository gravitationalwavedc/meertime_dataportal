import { aliasMutation, aliasQuery } from "../utils/graphql-test-utils";

describe("The Session Page", () => {
  beforeEach(() => {
    cy.intercept("http://localhost:8000/graphql/", (req) => {
      aliasMutation(req, "LoginMutation", "loginMutation.json");
      aliasQuery(req, "SessionQuery", "sessionQuery.json");
    });
    cy.visit("/session/2419/");
    cy.location("pathname").should("equal", "/login");

    cy.get("input[name=username]").type("buffy@sunnydale.com");
    cy.get("input[name=password]").type("slayer!#1");
    cy.contains("button", "Sign in").click();

    cy.wait("@LoginMutation")
      .its("response.body.data.tokenAuth")
      .should("have.property", "token");
  });

  it("displays loading then the data", () => {
    cy.contains("Sessions").should("be.visible");
    cy.contains("Loading...").should("be.visible");

    cy.wait("@SessionQuery");

    cy.contains("Loading...").should("not.exist");
    cy.contains("JName").should("be.visible");
    cy.location("pathname").should("equal", "/session/2419/");
  });
});
