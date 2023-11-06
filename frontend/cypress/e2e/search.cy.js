import { aliasMutation, aliasQuery } from "../utils/graphql-test-utils";

describe("The Search Page", () => {
  beforeEach(() => {
    cy.intercept("http://localhost:8000/graphql/", (req) => {
      aliasMutation(req, "LoginMutation", "loginMutation.json");
      aliasQuery(req, "SearchQuery", "searchQuery.json");
      aliasQuery(req, "SearchTableQuery", "searchQueryFewer.json");
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

  it("changes band when selected", () => {
    cy.wait("@SearchQuery");
    cy.get('table').get('tbody').find('tr').should('have.length', 3);

    cy.get('#bandSelect').select("LBAND", {force: true});

    cy.wait("@SearchTableQuery");
    // cy.url().should('eq', 'http://localhost:5173/?search=&mainProject=meertime&mostCommonProject=All&band=LBAND');
    cy.get('table').get('tbody').find('tr').should('have.length', 2);
  });

  it("changes project when selected", () => {
    cy.wait("@SearchQuery");
    cy.get('table').get('tbody').find('tr').should('have.length', 3);

    cy.get('#projectSelect').select("PTA", {force: true});

    cy.wait("@SearchTableQuery");
    // cy.url().should('eq', 'http://localhost:5173/?search=&mainProject=trapum&mostCommonProject=All&band=All');
    cy.get('table').get('tbody').find('tr').should('have.length', 2);
  });
});
