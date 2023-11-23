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

const sessionTableQuery = graphql`
  fragment SessionTable_data on Query
  @refetchable(queryName: "SessionTableQuery")
  @argumentDefinitions(
    start: { type: "String" }
    end: { type: "String" }
    utc: { type: "String" }
    project: { type: "String", defaultValue: "All" }
  ) {
    sessionDisplay(start: $start, end: $end, utc: $utc) {
      start
      end
      numberOfObservations
      numberOfPulsars
      sessionPulsars(project: $project) {
        edges {
          node {
            jname
            pulsarType
            project
            utc
            beam
            integrations
            frequency
            backendSN
            fluxHi
            phaseVsTimeHi
            phaseVsFrequencyHi
            fluxLo
            phaseVsTimeLo
            phaseVsFrequencyLo
          }
        }
      }
    }
  }
`;

const SessionTable = ({ data, utc }) => {
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
    if (utc !== undefined) {
      refetch({ start: null, end: null, utc: utc, project: project });
    } else {
      refetch({
        start: fragmentData.sessionDisplay.start,
        end: fragmentData.sessionDisplay.end,
        utc: null,
        project: project,
      });
    }
  }, [project, utc, refetch, fragmentData.sessionDisplay]);

  const startDate = moment
    .parseZone(fragmentData.sessionDisplay.start, moment.ISO_8601)
    .format("h:mma DD/MM/YYYY");
  const endDate = moment
    .parseZone(fragmentData.sessionDisplay.end, moment.ISO_8601)
    .format("h:mma DD/MM/YYYY");

  const openLightBox = (images, imageIndex) => {
    setIsLightBoxOpen(true);
    setLightBoxImages({ images: images, imagesIndex: imageIndex });
  };

  const rows = fragmentData.sessionDisplay.sessionPulsars.edges.reduce(
    (result, edge) => {
      const row = { ...edge.node };
      row.utc = formatUTC(row.utc);
      row.projectKey = project;

      const images = [
        `${import.meta.env.VITE_DJANGO_MEDIA_URL}${row.fluxHi}`,
        `${import.meta.env.VITE_DJANGO_MEDIA_URL}${row.phaseVsTimeHi}`,
        `${import.meta.env.VITE_DJANGO_MEDIA_URL}${row.phaseVsFrequencyHi}`,
      ];

      row.flux = (
        <SessionImage
          imageHi={row.fluxHi}
          imageLo={row.fluxLo}
          images={images}
          imageIndex={0}
          openLightBox={openLightBox}
        />
      );
      row.phaseVsTime = (
        <SessionImage
          imageHi={row.phaseVsTimeHi}
          imageLo={row.phaseVsTimeLo}
          images={images}
          imageIndex={1}
          openLightBox={openLightBox}
        />
      );
      row.phaseVsFrequency = (
        <SessionImage
          imageHi={row.phaseVsFrequencyHi}
          imageLo={row.phaseVsFrequencyLo}
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
    },
    []
  );

  const columns = [
    { dataField: "jname", text: "JName", sort: true },
    {
      dataField: "project",
      text: "Project",
      sort: true,
      screenSizes: ["md", "lg", "xl", "xxl"],
    },
    { dataField: "utc", text: "UTC", sort: true, screenSizes: ["xl", "xxl"] },
    {
      dataField: "backendSN",
      text: "Backend S/N",
      align: "right",
      headerAlign: "right",
      sort: true,
      screenSizes: ["xl", "xxl"],
    },
    {
      dataField: "integrations",
      text: "Integration",
      align: "right",
      headerAlign: "right",
      sort: true,
      formatter: (cell) => `${cell} [s]`,
      screenSizes: ["xl", "xxl"],
    },
    {
      dataField: "frequency",
      text: "Frequency",
      align: "right",
      headerAlign: "right",
      sort: true,
      formatter: (cell) => `${cell} Mhz`,
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

  const projectData = fragmentData.sessionDisplay.sessionPulsars.edges.reduce(
    (result, edge) => {
      if (
        result.filter((project) => project.title === edge.node.project)
          .length === 0
      ) {
        return [
          ...result,
          {
            title: edge.node.project,
            value: fragmentData.sessionDisplay.sessionPulsars.edges.filter(
              (newEdge) => newEdge.node.project === edge.node.project
            ).length,
          },
        ];
      }

      return result;
    },
    []
  );

  const summaryData = [
    {
      title: "Observations",
      value: fragmentData.sessionDisplay.numberOfObservations,
    },
    { title: "Pulsars", value: fragmentData.sessionDisplay.numberOfPulsars },
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
