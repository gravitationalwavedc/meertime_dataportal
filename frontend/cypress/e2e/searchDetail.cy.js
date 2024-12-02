import { aliasQuery } from "../utils/graphql-test-utils";

describe("The Search Detail Page", () => {
  beforeEach(() => {
    cy.intercept("http://localhost:8000/graphql/", (req) => {
      aliasQuery(req, "SearchDetailQuery", "searchDetailQuery.json");
    });
    cy.visit("search/All/J1944+1755/");
  });

  it("displays loading then the data", () => {
    cy.contains("J1944+1755").should("be.visible");
    cy.wait("@SearchDetailQuery");

    cy.contains("Loading...").should("not.exist");
    cy.contains("Timestamp").should("be.visible");
    cy.location("pathname").should("equal", "/search/All/J1944+1755/");
  });

  it("changes project when selected", () => {
    cy.wait("@SearchDetailQuery");
    cy.get("table").get("tbody").find("tr").should("have.length", 1);

    cy.get("#projectSelect").select("PTA", { force: true });
    cy.get("table").contains("GC").should("not.exist");
  });
});
