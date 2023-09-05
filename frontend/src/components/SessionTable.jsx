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
import image404 from "../assets/images/image404.png";


const sessionTableQuery = graphql`
  fragment SessionTable_data on Query
  @argumentDefinitions(
    id: { type: "Int" }
  ) {
    observationSummary (
      pulsar_Name: "All",
      obsType: "All",
      calibrationInt: $id,
      project_Short: "All",
      telescope_Name: "All",
    ) {
      edges {
        node {
          observations
          projects
          pulsars
        }
      }
    }
    calibration (id: $id) {
      edges {
        node {
          id
          idInt
          start
          end
          observations {
            edges {
              node {
                id
                pulsar {
                  name
                }
                utcStart
                obsType
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
`;


const SessionTable = ({ data: { observationSummary, calibration }, relay, id }) => {
  const [fragmentData, refetch] = useRefetchableFragment(
    sessionTableQuery,
    data
  );
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

    if (row.pulsarFoldResults.edges.length === 0) {
      return [...result];
    }
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
      flux             ? `${import.meta.env.VITE_DJANGO_MEDIA_URL}${flux.url}`             : image404,
      phaseVsTime      ? `${import.meta.env.VITE_DJANGO_MEDIA_URL}${phaseVsTime.url}`      : image404,
      phaseVsFrequency ? `${import.meta.env.VITE_DJANGO_MEDIA_URL}${phaseVsFrequency.url}` : image404,
    ];

    row.flux = (
      <SessionImage
        imageHi={flux}
        imageLo={flux}
        images={images}
        imageIndex={0}
        openLightBox={openLightBox}
      />
    );
    row.phaseVsTime = (
      <SessionImage
        imageHi={phaseVsTime}
        imageLo={phaseVsTime}
        images={images}
        imageIndex={1}
        openLightBox={openLightBox}
      />
    );
    row.phaseVsFrequency = (
      <SessionImage
        imageHi={phaseVsFrequency}
        imageLo={phaseVsFrequency}
        images={images}
        imageIndex={2}
        openLightBox={openLightBox}
      />
    );
    row.action = (
      <ButtonGroup vertical>
        <Link
          to={`/${row.obsType}/meertime/${row.pulsar.name}/`}
          size="sm"
          variant="outline-secondary"
          as={Button}
        >
          View all
        </Link>
        <Link
          to={`/${row.pulsar.name}/${row.utc}/${row.beam}/`}
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
      formatter: (cell) => cell ? cell.toFixed(1) : NaN,
      screenSizes: ["xl", "xxl"],
    },
    {
      dataField: "duration",
      text: "Duration",
      align: "right",
      headerAlign: "right",
      sort: true,
      formatter: (cell) => cell ? `${cell.toFixed(1)} [s]` : NaN,
      screenSizes: ["xl", "xxl"],
    },
    {
      dataField: "frequency",
      text: "Frequency",
      align: "right",
      headerAlign: "right",
      sort: true,
      formatter: (cell) => cell ? `${cell.toFixed(1)} [Mhz]` : NaN,
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

  const seenProjects = new Set();
  const projectData = calibration_node.observations.edges.reduce(
    (result, edge) => {
      if (!seenProjects.has(edge.node.project.short)) {
        seenProjects.add(edge.node.project.short);
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
    { title: "Observations", value: observationSummary.edges[0]?.node.observations },
    { title: "Pulsars", value: observationSummary.edges[0]?.node.pulsars },
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

export default SessionTable;