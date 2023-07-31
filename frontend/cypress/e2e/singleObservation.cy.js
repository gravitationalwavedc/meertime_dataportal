import { aliasMutation, aliasQuery } from "../utils/graphql-test-utils";

describe("Single Observation Page", () => {
  beforeEach(() => {
    cy.intercept("http://localhost:8000/graphql/", (req) => {
      aliasMutation(req, "LoginMutation", "loginMutation.json");
    });

    cy.visit("/J0125-2327/2020-02-04-00:21:21/2/");

    cy.get("input[name=username]").type("buffy@sunnydale.com");
    cy.get("input[name=password]").type("slayer!#1");
    cy.contains("button", "Sign in").click();

    cy.wait("@LoginMutation")
      .its("response.body.data.tokenAuth")
      .should("have.property", "token");
  });

  it("should display the download buttons where there are files", () => {
    cy.intercept("http://localhost:8000/graphql/", (req) => {
      aliasQuery(req, "SingleObservationQuery", "foldObservationDetails.json");
    });

    cy.wait("@SingleObservationQuery");

    // Correct page loads
    cy.contains("Loading...").should("not.exist");
    cy.contains("J0125-2327").should("be.visible");

    // The download buttons are visible
    cy.contains("Download Fluxcal Archive").should("be.visible");
    // The images have been loaded

    cy.get("img[alt='Plot flux using raw data.']").should(
      "have.attr",
      "src",
      "http://localhost:8000/media/MeerKAT/J0125-2327/2023-05-10-05:28:55/2/flux.hi.png"
    );
  });

  it("should hide download buttons when there are no files", () => {
    cy.intercept("http://localhost:8000/graphql/", (req) => {
      aliasQuery(
        req,
        "SingleObservationQuery",
        "foldObservationDetailsNoFiles.json"
      );
    });

    cy.wait("@SingleObservationQuery");

    // Download buttons should not show.
    cy.contains("Download Fluxcal Archive").should("not.exist");
  });
});
