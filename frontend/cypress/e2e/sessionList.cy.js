import { aliasQuery } from "../utils/graphql-test-utils";

describe("The Session List Page", () => {
  beforeEach(() => {
    cy.intercept("http://localhost:8000/graphql/", (req) => {
      aliasQuery(req, "SessionListTableQuery", "sessionListQuery.json");
      aliasQuery(req, "SessionQuery", "sessionQuery.json");
    });
    cy.visit("/sessions/");
  });

  it("displays loading then the data", () => {
    cy.contains("Sessions").should("be.visible");

    cy.wait("@SessionListTableQuery");

    cy.contains("Loading...").should("not.exist");
    cy.contains("Start").should("be.visible");
    cy.location("pathname").should("equal", "/sessions/");
  });

  it("check view all button", () => {
    cy.wait("@SessionListTableQuery");
    cy.contains("View all").click();
    cy.location("pathname").should("equal", "/session/64/");

    cy.wait("@SessionQuery");
    cy.contains("JName").should("be.visible");
  });
});
