import {
  aliasMutation,
  aliasQuery,
  aliasQueryWithVariables,
} from "../utils/graphql-test-utils";

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
      aliasQuery(req, "SingleObservationQuery", "foldObservationDetails.json");
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
    cy.get("table").get("tbody").find("tr").should("have.length", 3);

    cy.get("#bandSelect").select("LBAND", { force: true });

    cy.wait("@FoldTableRefetchQuery");
    cy.url().should(
      "eq",
      "http://localhost:5173/?search=&mainProject=meertime&project=All&band=LBAND"
    );
    cy.get("table").get("tbody").find("tr").should("have.length", 2);
  });

  it("changes main project when selected", () => {
    cy.wait("@FoldQuery");
    cy.get("table").get("tbody").find("tr").should("have.length", 3);

    cy.get("#mainProjectSelect").select("Trapum", { force: true });

    cy.wait("@FoldTableRefetchQuery");
    cy.url().should(
      "eq",
      "http://localhost:5173/?search=&mainProject=trapum&project=All&band=All"
    );
    cy.get("table").get("tbody").find("tr").should("have.length", 2);
  });

  it("changes project when selected", () => {
    cy.wait("@FoldQuery");
    cy.get("table").get("tbody").find("tr").should("have.length", 3);

    cy.get("#projectSelect").select("TPA", { force: true });

    cy.wait("@FoldTableRefetchQuery");
    cy.url().should(
      "eq",
      "http://localhost:5173/?search=&mainProject=meertime&project=TPA&band=All"
    );
    cy.get("table").get("tbody").find("tr").should("have.length", 2);
  });

  it("check view all button", () => {
    cy.wait("@FoldQuery");
    cy.contains("View all").click();
    cy.location("pathname").should("equal", "/fold/meertime/J1648-6044/");

    cy.wait("@FoldDetailQuery");

    cy.contains("Loading...").should("not.exist");
    cy.contains("PSR J0125-2327 is a millisecond pulsar").should("be.visible");
  });

  it("check view last button", () => {
    cy.wait("@FoldQuery");
    cy.contains("View last").click();
    cy.location("pathname").should(
      "equal",
      "/J1648-6044/2023-09-03-20:40:23/1/"
    );

    cy.wait("@SingleObservationQuery");
    cy.contains("Loading...").should("not.exist");
    cy.contains("Raw").should("be.visible");
  });
});
