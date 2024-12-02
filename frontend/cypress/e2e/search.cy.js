import { aliasQuery } from "../utils/graphql-test-utils";

describe("The Search Page", () => {
  beforeEach(() => {
    cy.intercept("http://localhost:8000/graphql/", (req) => {
      aliasQuery(req, "SearchQuery", "searchQuery.json");
      aliasQuery(req, "SearchTableQuery", "searchQueryFewer.json");
      aliasQuery(req, "SearchDetailQuery", "searchDetailQuery.json");
    });
    cy.visit("/search/");
  });

  it("displays loading then the data", () => {
    cy.contains("Search Mode Observations").should("be.visible");
    cy.wait("@SearchQuery");
    cy.contains("Loading...").should("not.exist");
    cy.contains("Pulsars").should("be.visible");
    cy.location("pathname").should("equal", "/search/");
  });

  it("changes band when selected", () => {
    cy.wait("@SearchQuery");
    cy.get("table").get("tbody").find("tr").should("have.length", 3);

    cy.get("#bandSelect").select("LBAND", { force: true });

    cy.wait("@SearchTableQuery");
    cy.get("table").get("tbody").find("tr").should("have.length", 2);
  });

  it("changes project when selected", () => {
    cy.wait("@SearchQuery");
    cy.get("table").get("tbody").find("tr").should("have.length", 3);

    cy.get("#projectSelect").select("PTA", { force: true });

    cy.wait("@SearchTableQuery");
    cy.get("table").get("tbody").find("tr").should("have.length", 2);
  });

  it("check view all button", () => {
    cy.wait("@SearchQuery");
    cy.contains("tr", "J1614+0737").contains("View all").click();
    cy.location("pathname").should("equal", "/search/All/J1614+0737/");

    cy.wait("@SearchDetailQuery");

    cy.contains("Loading...").should("not.exist");
    cy.contains("Timestamp").should("be.visible");
  });
});
