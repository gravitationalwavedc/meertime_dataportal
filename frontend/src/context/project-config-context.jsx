/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useEffect, useState } from "react";

const PROJECT_CONFIG_QUERY = `
  query projectConfigContextQuery {
    projectConfiguration {
      edges {
        node {
          id
          code
          short
          description
          displayOrder
          bandOptions
          plotTypes
          allowDownloads
          showExtendedObservationFields
          observationBandOverride
          toaMetadataAvailable
          useForFoldingAssets
          mainProject {
            id
            name
            telescope {
              id
              name
            }
          }
        }
      }
    }
  }
`;

const ProjectConfigContext = createContext({
  projects: [],
  isLoading: true,
});

const readProjects = (data) =>
  data?.projectConfiguration?.edges?.map(({ node }) => node).filter(Boolean) ??
  [];

const fetchProjectConfig = async (signal) => {
  const response = await fetch(import.meta.env.VITE_GRAPHQL_API, {
    method: "POST",
    headers: {
      Accept:
        "application/graphql-response+json; charset=utf-8, application/json; charset=utf-8",
      "Content-Type": "application/json",
    },
    credentials: "include",
    signal,
    body: JSON.stringify({ query: PROJECT_CONFIG_QUERY, variables: {} }),
  });

  if (!response.ok) {
    throw new Error("Unable to load project configuration");
  }

  return response.json();
};

export const ProjectConfigProvider = ({ children }) => {
  const [projects, setProjects] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const controller = new AbortController();

    fetchProjectConfig(controller.signal)
      .then(({ data }) => {
        setProjects(readProjects(data));
        setIsLoading(false);
      })
      .catch(() => {
        if (!controller.signal.aborted) {
          setProjects([]);
          setIsLoading(false);
        }
      });

    // Cancel any in-flight catalogue request if the app provider unmounts.
    return () => controller.abort();
  }, []);

  return (
    <ProjectConfigContext.Provider value={{ projects, isLoading }}>
      {children}
    </ProjectConfigContext.Provider>
  );
};

export const useProjectConfig = () => useContext(ProjectConfigContext);
