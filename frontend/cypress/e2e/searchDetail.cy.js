import { aliasMutation, aliasQuery } from "../utils/graphql-test-utils";

describe("The Search Detail Page", () => {
  beforeEach(() => {
    cy.intercept("http://localhost:8000/graphql/", (req) => {
      aliasMutation(req, "LoginMutation", "loginMutation.json");
      aliasQuery(req, "SearchDetailQuery", "searchDetailQuery.json");
    });
    cy.visit("search/All/J1944+1755/");
    cy.location("pathname").should("equal", "/login");

    cy.get("input[name=username]").type("buffy@sunnydale.com");
    cy.get("input[name=password]").type("slayer!#1");
    cy.contains("button", "Sign in").click();

    cy.wait("@LoginMutation")
      .its("response.body.data.tokenAuth")
      .should("have.property", "token");
  });

  it("displays loading then the data", () => {
    cy.contains("J1944 1755").should("be.visible");
    cy.contains("Loading...").should("be.visible");

    cy.wait("@SearchDetailQuery");

    cy.contains("Loading...").should("not.exist");
    cy.contains("Timestamp").should("be.visible");
    cy.location("pathname").should("equal", "/search/All/J1944%201755/");
  });

  it("changes project when selected", () => {
    cy.wait("@SearchDetailQuery");
    cy.get("table").get("tbody").find("tr").should("have.length", 1);

    cy.get("#projectSelect").select("PTA", { force: true });
    cy.get("table").contains("GC").should("not.exist");
  });
});
