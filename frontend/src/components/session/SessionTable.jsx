import { Button, ButtonGroup, Badge, Col } from "react-bootstrap";
import { useState } from "react";
import { graphql, useFragment } from "react-relay";
import LightBox from "react-image-lightbox";

import { columnsSizeFilter, formatUTC } from "../../helpers";
import DataView from "../DataView";
import SessionCard from "./SessionCard";
import SessionImage from "./SessionImage";
import moment from "moment";
import { Link } from "found";
import { useScreenSize } from "../../context/screenSize-context";
import image404 from "../../assets/images/image404.png";

const sessionTableByIdQuery = graphql`
  fragment SessionTable_data on Query
  @argumentDefinitions(id: { type: "Int" }) {
    calibration(id: $id) {
      edges {
        node {
          id
          idInt
          start
          end
          badges {
            edges {
              node {
                name
                description
              }
            }
          }
          observations {
            edges {
              node {
                id
                pulsar {
                  name
                }
                utcStart
                beam
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

const sessionTableLatestQuery = graphql`
  fragment SessionTableLatest_data on Query {
    calibration(first: 1) {
      edges {
        node {
          id
          idInt
          start
          end
          badges {
            edges {
              node {
                name
                description
              }
            }
          }
          observations {
            edges {
              node {
                id
                pulsar {
                  name
                }
                utcStart
                beam
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

const SessionTable = ({ data, isLatestSessionRoute }) => {
  const sessionData = useFragment(
    isLatestSessionRoute ? sessionTableLatestQuery : sessionTableByIdQuery,
    data
  );
  const { screenSize } = useScreenSize();
  const [project] = useState("All");
  const [isLightBoxOpen, setIsLightBoxOpen] = useState(false);
  const [lightBoxImages, setLightBoxImages] = useState({
    images: [],
    imagesIndex: 0,
  });

  // Grab the single item from the edges array
  const calibration_node = sessionData.calibration?.edges?.[0]?.node;
  const observationEdges = calibration_node?.observations?.edges ?? [];
  const startDate = moment
    .parseZone(calibration_node?.start, moment.ISO_8601)
    .format("h:mma DD/MM/YYYY");
  const endDate = moment
    .parseZone(calibration_node?.end, moment.ISO_8601)
    .format("h:mma DD/MM/YYYY");

  const openLightBox = (images, imageIndex) => {
    setIsLightBoxOpen(true);
    setLightBoxImages({ images: images, imagesIndex: imageIndex });
  };

  const rows = observationEdges.reduce((result, edge) => {
    const row = { ...edge.node };
    row.utc = formatUTC(row.utcStart);
    row.projectKey = project;
    const pulsarFoldResultEdges = row.pulsarFoldResults?.edges ?? [];

    if (pulsarFoldResultEdges.length === 0) {
      row.sn = null;
      row.flux = null;
      row.phaseVsTime = null;
      row.phaseVsFrequency = null;
    } else {
      const pulsarFoldResult = pulsarFoldResultEdges[0]?.node;
      row.sn = pulsarFoldResult?.pipelineRun?.sn ?? null;

      // Grab the three images
      const imageEdges = pulsarFoldResult?.images?.edges ?? [];
      const flux = imageEdges.filter(
        (edge) => edge.node.imageType === "PROFILE" && edge.node.cleaned
      )[0]?.node;
      const phaseVsTime = imageEdges.filter(
        (edge) => edge.node.imageType === "PHASE_TIME" && edge.node.cleaned
      )[0]?.node;
      const phaseVsFrequency = imageEdges.filter(
        (edge) => edge.node.imageType === "PHASE_FREQ" && edge.node.cleaned
      )[0]?.node;
      const images = [
        flux ? `${flux.url}` : image404,
        phaseVsTime ? `${phaseVsTime.url}` : image404,
        phaseVsFrequency ? `${phaseVsFrequency.url}` : image404,
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
    }

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
        {pulsarFoldResultEdges.length !== 0 && (
          <Link
            to={`/meertime/${row.pulsar.name}/${row.utc}/${row.beam}/`}
            size="sm"
            variant="outline-secondary"
            as={Button}
          >
            View this
          </Link>
        )}
      </ButtonGroup>
    );
    return [...result, { ...row }];
  }, []);

  const columns = [
    { dataField: "pulsar.name", text: "JName", sort: true },
    {
      dataField: "obsType",
      text: "ObsType",
      sort: true,
      screenSizes: ["md", "lg", "xl", "xxl"],
    },
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
      screenSizes: ["xl", "xxl"],
    },
    {
      dataField: "sn",
      text: "S/N",
      align: "right",
      headerAlign: "right",
      sort: true,
      formatter: (cell) => (cell ? cell.toFixed(1) : NaN),
      screenSizes: ["xl", "xxl"],
    },
    {
      dataField: "duration",
      text: "Duration",
      align: "right",
      headerAlign: "right",
      sort: true,
      formatter: (cell) => (cell ? `${cell.toFixed(1)} [s]` : NaN),
      screenSizes: ["xl", "xxl"],
    },
    {
      dataField: "frequency",
      text: "Frequency",
      align: "right",
      headerAlign: "right",
      sort: true,
      formatter: (cell) => (cell ? `${cell.toFixed(1)} [Mhz]` : NaN),
      screenSizes: ["xxl"],
    },
    {
      dataField: "flux",
      text: "",
      align: "center",
      headerAlign: "center",
      sort: false,
      toggle: false,
    },
    {
      dataField: "phaseVsTime",
      text: "",
      align: "center",
      headerAlign: "center",
      sort: false,
      screenSizes: ["sm", "md", "lg", "xl", "xxl"],
      toggle: false,
    },
    {
      dataField: "phaseVsFrequency",
      text: "",
      align: "center",
      headerAlign: "center",
      sort: false,
      screenSizes: ["sm", "md", "lg", "xl", "xxl"],
      toggle: false,
    },
    {
      dataField: "action",
      text: "",
      align: "right",
      headerAlign: "right",
      sort: false,
      toggle: false,
    },
  ];

  const columnsSizeFiltered = columnsSizeFilter(columns, screenSize);

  const seenProjects = new Set();
  const projectData = observationEdges.reduce((result, edge) => {
    if (!seenProjects.has(edge.node.project.short)) {
      seenProjects.add(edge.node.project.short);
      return [
        ...result,
        {
          title: edge.node.project.short,
          value: observationEdges.filter(
            (newEdge) => newEdge.node.project.short === edge.node.project.short
          ).length,
        },
      ];
    }

    return result;
  }, []);

  const summaryData = [
    {
      title: "Observations",
      value: observationEdges.length,
    },
    {
      title: "Pulsars",
      value: new Set(observationEdges.map((edge) => edge.node.pulsar.name))
        .size,
    },
    ...projectData,
  ];

  const badges = calibration_node?.badges?.edges ?? [];

  return (
    <div className="session-table">
      <h5 style={{ marginTop: "-12rem", marginBottom: "10rem" }}>
        {startDate} UTC - {endDate} UTC
      </h5>
      <Col>
        {badges.map((badge) => (
          <Badge key={badge.node.name} variant="primary" className="mr-1">
            {badge.node.name}
          </Badge>
        ))}
      </Col>
      <DataView
        summaryData={summaryData}
        columns={columnsSizeFiltered}
        rows={rows}
        project={project}
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
          onImageLoad={() => {
            window.dispatchEvent(new Event("resize"));
          }}
        />
      )}
    </div>
  );
};

export default SessionTable;
