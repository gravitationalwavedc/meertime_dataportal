import { Button, ButtonGroup, Image } from 'react-bootstrap';
import React, { useEffect, useState } from 'react';
import { columnsSizeFilter, formatUTC } from '../helpers';
import { createRefetchContainer, graphql } from 'react-relay';

import DataView from './DataView';
import Link from 'found/Link';
import MainLayout from '../components/MainLayout';
import SessionCard from './SessionCard';
import image404 from '../assets/images/image404.png';
import moment from 'moment';
import { useScreenSize } from '../context/screenSize-context';

const SessionTable = ({ data: { relaySessions }, relay }) => {
    const { screenSize } = useScreenSize();
    const [project, setProject] = useState('meertime');

    useEffect(() => {
        relay.refetch({ getProposalFilters: project });
    }, [project, relay]);

    const startDate = moment.parseZone(relaySessions.first, moment.ISO_8601).format('h:mma DD/MM/YYYY');
    const endDate = moment.parseZone(relaySessions.last, moment.ISO_8601).format('h:mma DD/MM/YYYY');

    const rows = relaySessions.edges.reduce((result, edge) => { 
        const row = { ...edge.node };
        row.utc = formatUTC(row.utc);
        row.projectKey = project;
        row.length = `${row.length} [s]`;
        row.frequency= `${row.frequency} MHz`;
        row.profile = <Image rounded fluid src={row.profile.length > 0 ? `http://localhost:8000/media/${row.profile}` : image404}/>;
        row.phaseVsTime = <Image rounded fluid src={row.profile.length > 0 ? `http://localhost:8000/media/${row.phaseVsTime}` : image404}/>;
        row.phaseVsFrequency = <Image rounded fluid src={row.profile.length > 0 ? `http://localhost:8000/media/${row.phaseVsFrequency}` : image404}/>;
        row.action = <ButtonGroup vertical>
            <Link 
                to={`/fold/${project}/${row.jname}/`} 
                size='sm' 
                variant="outline-secondary" as={Button}>
                  View
            </Link>
            <Link 
                to={`/${row.jname}/${row.utc}/${row.beam}/`} 
                size='sm' 
                variant="outline-secondary" 
                as={Button}>
                  View last
            </Link>
        </ButtonGroup>;
        return [ ...result, { ...row }];
    }, []);

    const columns = [
        { dataField: 'jname', text: 'JName', sort:true },
        { dataField: 'proposalShort', text: 'Project', sort: true, screenSizes: ['md', 'lg', 'xl', 'xxl'] },
        { dataField: 'utc', text: 'UTC', sort: true, screenSizes: ['xl', 'xxl'] },
        { dataField: 'snrSpip', text: 'Backend S/N', align: 'right', headerAlign: 'right', sort: true, 
            screenSizes: ['xl', 'xxl'] },
        { dataField: 'length', text: 'Integration', align: 'right', headerAlign: 'right', sort: true,
            screenSizes: ['xl', 'xxl'] },
        { dataField: 'frequency', text: 'Frequency', align: 'right', headerAlign: 'right', sort: true, 
            screenSizes: ['xxl'] },
        { dataField: 'profile', text: 'Profile', align: 'center', headerAlign: 'center', sort: false },
        { dataField: 'phaseVsTime', text: 'Phase vs time', align: 'center', headerAlign: 'center', sort: false, 
            screenSizes: ['sm', 'md', 'lg', 'xl', 'xxl'] },
        { 
            dataField: 'phaseVsFrequency', 
            text: 'Phase vs frequency', 
            align: 'center', 
            headerAlign: 'center', 
            sort: false,
            screenSizes: ['sm', 'md', 'lg', 'xl', 'xxl']
        },
        { dataField: 'action', text: '', align: 'center', headerAlign: 'center', sort: false }
    ];

    const columnsSizeFiltered = columnsSizeFilter(columns, screenSize);

    const summaryData = [
        { title: 'Observations', value: relaySessions.nobs },
        { title: 'Pulsars', value: relaySessions.npsr },
        ...relaySessions.proposals.map(x => ({ title: x.name, value: x.count }))
    ]; 

    return(
        <MainLayout title='Last Session' subtitle={`${startDate} to ${endDate}`}>
            <div className="session-table">
                <DataView
                    summaryData={summaryData}
                    columns={columnsSizeFiltered}
                    rows={rows}
                    project={project}
                    setProject={setProject}
                    card={SessionCard}/>
            </div>
        </MainLayout>
    );
};

export default createRefetchContainer(
    SessionTable,
    {
        data: graphql`
          fragment SessionTable_data on Query @argumentDefinitions(
            getProposalFilters: {type: "String", defaultValue: "meertime"}
          ) {
            relaySessions(getProposalFilters: $getProposalFilters) {
              first
              last
              nobs
              npsr
              proposals {
                name
                count
              }
              edges {
                node {
                  jname
                  utc
                  proposalShort
                  snrSpip
                  length
                  beam
                  frequency
                  profile
                  phaseVsTime
                  phaseVsFrequency
                }
              }
            }
          }`
    },
    graphql`
      query SessionTableRefetchQuery($getProposalFilters: String) {
        ...SessionTable_data@arguments(getProposalFilters:$getProposalFilters)
      }
   `
);
