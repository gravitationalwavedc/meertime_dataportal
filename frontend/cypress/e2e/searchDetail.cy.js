import {
  aliasQuery,
  assertEmptyStringOrConcrete,
  assertNoAllValues,
} from "../utils/graphql-test-utils";

const SEARCH_DETAIL_GUARDED_KEYS = ["mainProject"];

describe("The Search Detail Page", () => {
  beforeEach(() => {
    cy.intercept("http://localhost:5173/api/graphql/", (req) => {
      if (req.body?.query?.includes("SearchDetailQuery")) {
        assertNoAllValues(req, SEARCH_DETAIL_GUARDED_KEYS, "SearchDetailQuery");
        assertEmptyStringOrConcrete(
          req,
          SEARCH_DETAIL_GUARDED_KEYS,
          "SearchDetailQuery"
        );
      }

      aliasQuery(req, "SearchDetailQuery", "searchDetailQuery.json");
    });

    // Mock session-based authentication endpoints to prevent leaking requests
    cy.intercept("GET", "/api/auth/session/", {
      statusCode: 200,
      body: {
        isAuthenticated: false,
        user: null
      }
    }).as("checkSession");

    cy.intercept("GET", "/api/auth/csrf/", {
      statusCode: 200,
      body: { csrfToken: "mock-csrf-token" }
    }).as("getCSRF");

    cy.visit("search/All/J1944+1755/");
  });

  it("displays loading then the data", () => {
    cy.contains("J1944+1755").should("be.visible");
    cy.wait("@SearchDetailQuery").then((interception) => {
      expect(interception.request.body.variables).to.deep.include({
        mainProject: "",
      });
    });

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
