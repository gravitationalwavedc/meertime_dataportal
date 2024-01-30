import { aliasMutation, aliasQuery } from "../utils/graphql-test-utils";

describe("The Fold Page", () => {
  beforeEach(() => {
    cy.intercept("http://localhost:8000/graphql/", (req) => {
      aliasMutation(req, "LoginMutation", "loginMutation.json");
      aliasQuery(req, "FoldQuery", "foldQuery.json");
      aliasQuery(req, "FoldTableRefetchQuery", "foldQueryFewer.json");
      aliasQuery(req, "FoldDetailQuery", "foldDetailQuery.json");
      aliasQuery(
        req,
        "FoldDetailFileDownloadQuery",
        "foldDetailFileDownloadQuery.json"
      );
      aliasQuery(req, "SingleObservationQuery", "singleObservationQuery.json");
      aliasQuery(
        req,
        "SingleObservationFileDownloadQuery",
        "singleObservationFileDownloadQuery.json"
      );
    });
    cy.visit("/");
    cy.location("pathname").should("equal", "/login");

    cy.get("input[name=username]").type("buffy@sunnydale.com");
    cy.get("input[name=password]").type("slayer!#1");
    cy.contains("button", "Sign in").click();

    cy.wait("@LoginMutation")
      .its("response.body.data.tokenAuth")
      .should("have.property", "token");
  });

  it("displays loading then the data", () => {
    cy.contains("Fold Observations").should("be.visible");
    cy.contains("Loading...").should("be.visible");

    cy.wait("@FoldQuery");

    cy.contains("Loading...").should("not.exist");
    cy.contains("Unique Pulsars").should("be.visible");
    cy.location("pathname").should("equal", "/");
  });

  it("changes band when selected", () => {
    cy.wait("@FoldQuery");
    cy.get("table").get("tbody").find("tr").should("have.length", 2);

    cy.get("#bandSelect").select("LBAND", { force: true });

    cy.wait("@FoldTableRefetchQuery");
    cy.url().should(
      "eq",
      "http://localhost:5173/?search=&mainProject=meertime&mostCommonProject=All&project=All&band=LBAND"
    );
    cy.get("table").get("tbody").find("tr").should("have.length", 1);
  });

  it("changes main project when selected", () => {
    cy.wait("@FoldQuery");
    cy.get("table").get("tbody").find("tr").should("have.length", 2);

    cy.get("#mainProjectSelect").select("Trapum", { force: true });

    cy.wait("@FoldTableRefetchQuery");
    cy.url().should(
      "eq",
      "http://localhost:5173/?search=&mainProject=trapum&mostCommonProject=All&project=All&band=All"
    );
    cy.get("table").get("tbody").find("tr").should("have.length", 1);
  });

  it("changes project when selected", () => {
    cy.wait("@FoldQuery");
    cy.get("table").get("tbody").find("tr").should("have.length", 2);

    cy.get("#projectSelect").select("TPA", { force: true });

    cy.wait("@FoldTableRefetchQuery");
    cy.url().should(
      "eq",
      "http://localhost:5173/?search=&mainProject=meertime&mostCommonProject=All&project=TPA&band=All"
    );
    cy.get("table").get("tbody").find("tr").should("have.length", 1);
  });

  it("changes most common project when selected", () => {
    cy.wait("@FoldQuery");
    cy.get("table").get("tbody").find("tr").should("have.length", 2);

    cy.get("#mostCommonProjectSelect").select("TPA", { force: true });

    cy.wait("@FoldTableRefetchQuery");
    cy.url().should(
      "eq",
      "http://localhost:5173/?search=&mainProject=meertime&mostCommonProject=TPA&project=All&band=All"
    );
    cy.get("table").get("tbody").find("tr").should("have.length", 1);
  });

  it("check view all button", () => {
    cy.wait("@FoldQuery");
    cy.contains("tr", "J0125-2327").contains("View all").click();
    cy.location("pathname").should("equal", "/fold/meertime/J0125-2327/");

    cy.wait("@FoldDetailQuery");

    cy.contains("Loading...").should("not.exist");
    cy.contains("PSR J0125-2327 is a millisecond pulsar").should("be.visible");
  });

  it("check view last button", () => {
    cy.wait("@FoldQuery");
    cy.contains("tr", "2020-07-10-05").contains("View last").click();
    cy.location("pathname").should(
      "equal",
      "/meertime/J0125-2327/2020-07-10-05:07:28/2/"
    );

    cy.wait("@SingleObservationQuery");
    cy.contains("Loading...").should("not.exist");
    cy.contains("Raw").should("be.visible");
  });
});
