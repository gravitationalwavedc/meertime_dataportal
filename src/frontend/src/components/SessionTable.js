import { Button, ButtonGroup, Image } from 'react-bootstrap';
import React, { useEffect, useState } from 'react';
import { createRefetchContainer, graphql } from 'react-relay';

import DataView from './DataView';
import Link from 'found/Link';
import MainLayout from '../components/MainLayout';
import { formatUTC } from '../helpers';
import image404 from '../assets/images/image404.png';
import moment from 'moment';

const SessionTable = ({ data: { relaySessions }, relay }) => {
    const [project, setProject] = useState('meertime');

    useEffect(() => {
        relay.refetch({ getProposalFilters: project });
    }, [project, relay]);

    const startDate = moment.parseZone(relaySessions.first, moment.ISO_8601).format('h:mma DD/MM/YYYY');
    const endDate = moment.parseZone(relaySessions.last, moment.ISO_8601).format('h:mma DD/MM/YYYY');

    const rows = relaySessions.edges.reduce((result, edge) => { 
        const row = { ...edge.node };
        row.utc = formatUTC(row.utc);
        row.profile = <Image rounded fluid src={row.profile.length > 0 ? `http://localhost:8000/media/${row.profile}` : image404}/>;
        row.phaseVsTime = <Image rounded fluid src={row.profile.length > 0 ? `http://localhost:8000/media/${row.phaseVsTime}` : image404}/>;
        row.phaseVsFrequency = <Image rounded fluid src={row.profile.length > 0 ? `http://localhost:8000/media/${row.phaseVsFrequency}` : image404}/>;
        row.action = <ButtonGroup vertical>
            <Link 
                to={`/fold/${project}/${row.jname}/`} 
                size='sm' 
                variant="outline-secondary" as={Button}>
                  View all
            </Link>
            <Link 
                to={`/${row.jname}/${row.utc}/${row.beam}/`} 
                size='sm' 
                variant="outline-secondary" 
                as={Button}>
                  View Last
            </Link>
        </ButtonGroup>;
        return [ ...result, { ...row }];
    }, []);

    const columns = [
        { dataField: 'jname', text: 'JName', sort:true },
        { dataField: 'proposalShort', text: 'Project', sort: true },
        { dataField: 'utc', text: 'UTC', sort: true },
        { dataField: 'snrSpip', text: 'Backend S/N', align: 'right', headerAlign: 'right', sort: true },
        { dataField: 'length', text: 'Integration', align: 'right', headerAlign: 'right', sort: true },
        { dataField: 'frequency', text: 'Frequency', align: 'right', headerAlign: 'right', sort: true },
        { dataField: 'profile', text: '', align: 'center', headerAlign: 'center', sort: false },
        { dataField: 'phaseVsTime', text: '', align: 'center', headerAlign: 'center', sort: false },
        { dataField: 'phaseVsFrequency', text: '', align: 'center', headerAlign: 'center', sort: false },
        { dataField: 'action', text: '', align: 'center', headerAlign: 'center', sort: false }
    ];

    const summaryData = [
        { title: 'Observations', value: relaySessions.nobs },
        { title: 'Pulsars', value: relaySessions.npsr },
        { title: 'PA', value: 8 },
        { title: 'TPA', value: 4 }
    ];

    return(
        <MainLayout title='Last Session' subtitle={`${startDate} to ${endDate}`}>
            <DataView
                summaryData={summaryData}
                columns={columns}
                rows={rows}
                project={project}
                setProject={setProject} />
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
