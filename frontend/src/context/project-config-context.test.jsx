import { render, screen, waitFor } from "@testing-library/react";
import { vi } from "vitest";

import {
  ProjectConfigProvider,
  useProjectConfig,
} from "./project-config-context";

const fetchMock = vi.fn();

const fetchResult = (data) => ({
  ok: true,
  json: () => Promise.resolve({ data }),
});

const Consumer = () => {
  const { projects, isLoading } = useProjectConfig();
  return (
    <>
      <div data-testid="loading">{String(isLoading)}</div>
      <div data-testid="projects">
        {projects.map(({ code }) => code).join(",")}
      </div>
    </>
  );
};

const renderProvider = () =>
  render(
    <ProjectConfigProvider>
      <Consumer />
    </ProjectConfigProvider>
  );

const expectLoadedProjects = async (codes) => {
  await waitFor(() =>
    expect(screen.getByTestId("loading")).toHaveTextContent("false")
  );
  expect(screen.getByTestId("projects")).toHaveTextContent(codes);
};

describe("ProjectConfigProvider", () => {
  beforeEach(() => {
    fetchMock.mockReset();
    vi.stubGlobal("fetch", fetchMock);
  });

  it("exposes configured projects in query order", async () => {
    fetchMock.mockResolvedValue(
      fetchResult({
        projectConfiguration: {
          edges: [
            { node: { code: "FIRST" } },
            { node: { code: "SECOND" } },
            { node: { code: "THIRD" } },
          ],
        },
      })
    );

    renderProvider();

    await expectLoadedProjects("FIRST,SECOND,THIRD");
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/graphql/"),
      expect.objectContaining({
        credentials: "include",
        method: "POST",
      })
    );
  });

  it.each([
    ["empty query", () => fetchResult({ projectConfiguration: { edges: [] } })],
    ["query failure", () => Promise.reject(new Error("No catalogue today"))],
  ])("falls back to empty projects for %s", async (_, result) => {
    fetchMock.mockReturnValue(result());

    renderProvider();

    await expectLoadedProjects("");
  });
});
