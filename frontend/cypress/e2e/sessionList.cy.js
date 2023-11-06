import { aliasMutation, aliasQuery } from "../utils/graphql-test-utils";

describe("The Session List Page", () => {
  beforeEach(() => {
    cy.intercept("http://localhost:8000/graphql/", (req) => {
      aliasMutation(req, "LoginMutation", "loginMutation.json");
      aliasQuery(req, "SessionListTableQuery", "sessionListQuery.json");
      aliasQuery(req, "SessionQuery", "sessionQuery.json");
    });
    cy.visit("/sessions/");
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

    cy.wait("@SessionListTableQuery");

    cy.contains("Loading...").should("not.exist");
    cy.contains("Start").should("be.visible");
    cy.location("pathname").should("equal", "/sessions/");
  });

  it("check view all button", () => {
    cy.wait("@SessionListTableQuery");
    cy.contains("View all").click();
    cy.location("pathname").should("equal", "/session/3562/");

    cy.wait("@SessionQuery");
    cy.contains("JName").should("be.visible");
  });
});
