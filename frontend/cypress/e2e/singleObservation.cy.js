import { aliasMutation, aliasQuery } from "../utils/graphql-test-utils";

describe("Single Observation Page", () => {
  beforeEach(() => {
    cy.intercept("http://localhost:8000/graphql/", (req) => {
      aliasMutation(req, "LoginMutation", "loginMutation.json");
      aliasMutation(req, "RefreshTokenMutation", "refreshTokenMutation.json");
      aliasQuery(req, "SingleObservationQuery", "foldObservationDetails.json");
    });

    cy.visit("/meertime/J0125-2327/2023-04-29-06:47:34/2/");

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
    cy.location("pathname").should(
      "equal",
      "/meertime/J0125-2327/2023-04-29-06:47:34/2/"
    );
  });

  it("should display the download buttons where there are files", () => {
    cy.wait("@SingleObservationQuery");

    // Correct page loads
    cy.contains("J0125-2327").should("be.visible");

    // The download buttons are visible
    cy.contains("Download Data Files").should("be.visible");
  });

  it("should render the page with images", () => {
    cy.wait("@SingleObservationQuery");

    cy.get('img[alt="Plot PROFILE raw"').should("be.visible");
    cy.get('img[alt="Plot PROFILE cleaned').should("be.visible");
    cy.get('img[alt="Plot PROFILE_POL raw').should("be.visible");
    cy.get('img[alt="Plot PROFILE_POL cleaned').should("be.visible");
    cy.get('img[alt="Plot PHASE_TIME raw').should("be.visible");
    cy.get('img[alt="Plot PHASE_TIME cleaned').should("be.visible");
    cy.get('img[alt="Plot PHASE_FREQ raw').should("be.visible");
    cy.get('img[alt="Plot PHASE_FREQ cleaned').should("be.visible");
    cy.get('img[alt="Plot BANDPASS raw').should("be.visible");
    cy.get('img[alt="Plot BANDPASS cleaned').should("be.visible");
    cy.get('img[alt="Plot SNR_CUMUL raw').should("be.visible");
    cy.get('img[alt="Plot SNR_CUMUL cleaned').should("be.visible");
    cy.get('img[alt="Plot SNR_SINGLE raw').should("be.visible");
    cy.get('img[alt="Plot SNR_SINGLE cleaned').should("be.visible");
  });

  it("should render even without images", () => {
    cy.intercept("http://localhost:8000/graphql/", (req) => {
      aliasQuery(
        req,
        "SingleObservationQuery",
        "singleObservationQueryNoImages.json"
      );
    });
    cy.wait("@SingleObservationQuery");

    cy.contains("J0125-2327").should("be.visible");
  });
});
