import { aliasMutation, aliasQuery } from "../utils/graphql-test-utils";

describe("Single Observation Page", () => {
  beforeEach(() => {
    cy.intercept("http://localhost:8000/graphql/", (req) => {
      aliasMutation(req, "LoginMutation", "loginMutation.json");
      aliasMutation(req, "RefreshTokenMutation", "refreshTokenMutation.json");
      aliasQuery(req, "SingleObservationQuery", "foldObservationDetails.json");
    });

    cy.visit("/J0125-2327/2023-04-29-06:47:34/2/");

    cy.get("input[name=username]").type("buffy@sunnydale.com");
    cy.get("input[name=password]").type("slayer!#1");
    cy.contains("button", "Sign in").click();

    cy.wait("@LoginMutation")
      .its("response.body.data.tokenAuth")
      .should("have.property", "token");
  });

  it("displays loading then the data", () => {
    cy.contains("J0125-2327").should("be.visible");
    cy.contains("Loading...").should("be.visible");

    cy.wait("@SingleObservationQuery");

    cy.contains("Loading...").should("not.exist");
    cy.contains("Raw").should("be.visible");
    cy.location("pathname").should("equal", "/J0125-2327/2023-04-29-06:47:34/2/");
  });

  it("should display the download buttons where there are files", () => {

    cy.visit("/J0125-2327/2023-04-29-06:47:34/2/");

    cy.wait("@SingleObservationQuery");

    // Correct page loads
    cy.contains("J0125-2327").should("be.visible");

    // The download buttons are visible
    cy.contains("Download Fluxcal Archive").should("be.visible");
  });

  it("should hide download buttons when there are no files", () => {
    cy.intercept("http://localhost:8000/graphql/", (req) => {
      aliasQuery(
        req,
        "SingleObservationQuery",
        "foldObservationDetailsNoFiles.json"
      );
    });

    cy.visit("/J0125-2327/2020-02-04-00:21:21/2/");

    cy.wait("@SingleObservationQuery");

    // Correct page loads
    cy.contains("J0125-2327").should("be.visible");

    // Download buttons should not show.
    cy.contains("Download Fluxcal Archive").should("not.exist");
  });
});
