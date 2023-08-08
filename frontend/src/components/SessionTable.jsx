import { Button, ButtonGroup } from "react-bootstrap";
import { useEffect, useState } from "react";
import { columnsSizeFilter, formatUTC } from "../helpers";
import { graphql, useRefetchableFragment } from "react-relay";

import DataView from "./DataView";
import LightBox from "react-image-lightbox";
import SessionCard from "./SessionCard";
import SessionImage from "./SessionImage";
import moment from "moment";
import { Link } from "found";
import { useScreenSize } from "../context/screenSize-context";

const SessionTable = ({ data: { calibration }, relay, id }) => {
  const { screenSize } = useScreenSize();
  const [project, setProject] = useState("All");
  const [isLightBoxOpen, setIsLightBoxOpen] = useState(false);
  const [lightBoxImages, setLightBoxImages] = useState({
    images: [],
    imagesIndex: 0,
  });

  useEffect(() => {
    if (id !== undefined) {
      relay.refetch({ id: null });
    } else {
      relay.refetch({
        id: id
      });
    }
  }, [project, relay, id]);

  // Grab the single item from the edges array
  const calibration_node = calibration.edges[0]?.node;
  const startDate = moment
    .parseZone(calibration_node.start, moment.ISO_8601)
    .format("h:mma DD/MM/YYYY");
  const endDate = moment
    .parseZone(calibration_node.end, moment.ISO_8601)
    .format("h:mma DD/MM/YYYY");

  const openLightBox = (images, imageIndex) => {
    setIsLightBoxOpen(true);
    setLightBoxImages({ images: images, imagesIndex: imageIndex });
  };

  const rows = calibration_node.observations.edges.reduce((result, edge) => {
    const row = { ...edge.node };
    row.utc = formatUTC(row.utcStart);
    row.projectKey = project;

    const pulsarFoldResult = row.pulsarFoldResults.edges[0]?.node;
    row.sn = pulsarFoldResult.pipelineRun.sn;

    // Grab the three images
    const flux = pulsarFoldResult.images.edges
      .filter(
        (edge) => edge.node.imageType === "PROFILE" && edge.node.cleaned
      )[0]?.node;
    const phaseVsTime = pulsarFoldResult.images.edges
      .filter(
        (edge) => edge.node.imageType === "PHASE_TIME" && edge.node.cleaned
      )[0]?.node;
    const phaseVsFrequency = pulsarFoldResult.images.edges
      .filter(
        (edge) => edge.node.imageType === "PHASE_FREQ" && edge.node.cleaned
      )[0]?.node;
    const images = [
      `${import.meta.env.VITE_DJANGO_MEDIA_URL}${flux.url}`,
      `${import.meta.env.VITE_DJANGO_MEDIA_URL}${phaseVsTime.url}`,
      `${import.meta.env.VITE_DJANGO_MEDIA_URL}${phaseVsFrequency.url}`,
    ];

    row.flux = (
      <SessionImage
        imageHi={flux.url}
        imageLo={flux.url}
        images={images}
        imageIndex={0}
        openLightBox={openLightBox}
      />
    );
    row.phaseVsTime = (
      <SessionImage
        imageHi={phaseVsTime.url}
        imageLo={phaseVsTime.url}
        images={images}
        imageIndex={1}
        openLightBox={openLightBox}
      />
    );
    row.phaseVsFrequency = (
      <SessionImage
        imageHi={phaseVsFrequency.url}
        imageLo={phaseVsFrequency.url}
        images={images}
        imageIndex={2}
        openLightBox={openLightBox}
      />
    );
    row.action = (
      <ButtonGroup vertical>
        <Link
          to={`/${row.pulsarType}/meertime/${row.jname}/`}
          size="sm"
          variant="outline-secondary"
          as={Button}
        >
          View all
        </Link>
        <Link
          to={`/${row.jname}/${row.utc}/${row.beam}/`}
          size="sm"
          variant="outline-secondary"
          as={Button}
        >
          View last
        </Link>
      </ButtonGroup>
    );
    return [...result, { ...row }];
  }, []);

  const columns = [
    { dataField: "pulsar.name", text: "JName", sort: true },
    {
      dataField: "project.short",
      text: "Project",
      sort: true,
      screenSizes: ["md", "lg", "xl", "xxl"],
    },
    {
      dataField: "utcStart",
      text: "UTC",
      sort: true,
      formatter: (cell) => formatUTC(cell),
      screenSizes: ["xl", "xxl"]
    },
    {
      dataField: "sn",
      text: "S/N",
      align: "right",
      headerAlign: "right",
      sort: true,
      formatter: (cell) => cell.toFixed(1),
      screenSizes: ["xl", "xxl"],
    },
    {
      dataField: "duration",
      text: "Duration",
      align: "right",
      headerAlign: "right",
      sort: true,
      formatter: (cell) => `${cell.toFixed(1)} [s]`,
      screenSizes: ["xl", "xxl"],
    },
    {
      dataField: "frequency",
      text: "Frequency",
      align: "right",
      headerAlign: "right",
      sort: true,
      formatter: (cell) => `${cell.toFixed(1)} [Mhz]`,
      screenSizes: ["xxl"],
    },
    {
      dataField: "flux",
      text: "",
      align: "center",
      headerAlign: "center",
      sort: false,
    },
    {
      dataField: "phaseVsTime",
      text: "",
      align: "center",
      headerAlign: "center",
      sort: false,
      screenSizes: ["sm", "md", "lg", "xl", "xxl"],
    },
    {
      dataField: "phaseVsFrequency",
      text: "",
      align: "center",
      headerAlign: "center",
      sort: false,
      screenSizes: ["sm", "md", "lg", "xl", "xxl"],
    },
    {
      dataField: "action",
      text: "",
      align: "right",
      headerAlign: "right",
      sort: false,
    },
  ];

  const columnsSizeFiltered = columnsSizeFilter(columns, screenSize);

  const projectData = calibration_node.observations.edges.reduce(
    (result, edge) => {
      if (
        result.filter((project) => project === edge.node.project.short)
          .length === 0
      ) {
        return [
          ...result,
          {
            title: edge.node.project.short,
            value: calibration_node.observations.edges.filter(
              (newEdge) => newEdge.node.project.short === edge.node.project.short
            ).length,
          },
        ];
      }

      return result;
    },
    []
  );

  const summaryData = [
    { title: "Observations", value: calibration_node.numberOfObservations },
    // { title: "Pulsars", value: calibration_node.numberOfPulsars },
    ...projectData,
  ];

  return (
    <div className="session-table">
      <h5 style={{ marginTop: "-12rem", marginBottom: "10rem" }}>
        {startDate} UTC - {endDate} UTC
      </h5>
      <DataView
        summaryData={summaryData}
        columns={columnsSizeFiltered}
        rows={rows}
        project={project}
        setProject={setProject}
        card={SessionCard}
      />
      {isLightBoxOpen && (
        <LightBox
          mainSrc={lightBoxImages.images[lightBoxImages.imagesIndex]}
          nextSrc={
            lightBoxImages.images[
              (lightBoxImages.imagesIndex + 1) % lightBoxImages.images.length
            ]
          }
          prevSrc={
            lightBoxImages.images[
              (lightBoxImages.imagesIndex + lightBoxImages.images.length - 1) %
                lightBoxImages.images.length
            ]
          }
          onCloseRequest={() => setIsLightBoxOpen(false)}
          onMovePrevRequest={() =>
            setLightBoxImages({
              images: lightBoxImages.images,
              imagesIndex:
                (lightBoxImages.imagesIndex +
                  lightBoxImages.images.length -
                  1) %
                lightBoxImages.images.length,
            })
          }
          onMoveNextRequest={() =>
            setLightBoxImages({
              images: lightBoxImages.images,
              imagesIndex:
                (lightBoxImages.imagesIndex + 1) % lightBoxImages.images.length,
            })
          }
        />
      )}
    </div>
  );
};

export default createRefetchContainer(
  SessionTable,
  {
    data: graphql`
      fragment SessionTable_data on Query
      @argumentDefinitions(
        id: { type: "Int" }
      ) {
        calibration (id: $id) {
          edges {
            node {
              id
              idInt
              start
              end
              allProjects
              nObservations
              nAntMin
              nAntMax
              totalIntegrationTimeSeconds
              observations {
                edges {
                  node {
                    id
                    pulsar {
                      name
                    }
                    utcStart
                    duration
                    frequency
                    project {
                      short
                    }
                    pulsarFoldResults {
                      edges {
                        node {
                          images {
                            edges {
                              node {
                                url
                                imageType
                                cleaned
                              }
                            }
                          }
                          pipelineRun {
                            sn
                            percentRfiZapped
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    `,
  },
  graphql`
    query SessionTableRefetchQuery(
      $id: Int
    ) {
      ...SessionTable_data
        @arguments(id: $id)
    }
  `
);
