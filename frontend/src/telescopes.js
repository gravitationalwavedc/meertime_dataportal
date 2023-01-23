import React from 'react';

const getSubProjectOptions = (subprojects) => subprojects.map(
    subproject => <option value={subproject} key={subproject}>{subproject}</option>
);

const getProject = (projectValue) => projectValue === molonglo.value ? molonglo : meertime;

const molonglo = {
    value: 'MONSPSR',
    title: 'Molonglo',
    subprojects: [
        'All',
        'Mo-NS',
        'Mo-EW',
    ],
    bandOptions: [
        'UHF-NS',
        'UHF-EW'
    ],
    columns: [
        { dataField: 'key', text: '', sort: false, hidden: true, toggle: false, csvExport: false },
        { dataField: 'plotLink', text: '', sort: false, hidden: true, toggle: false, csvExport: false },
        { dataField: 'utc', text: 'Timestamp', sort: true, headerClasses: 'fold-detail-utc' },
        {
            dataField: 'project', text: 'Project', sort: true,
            screenSizes: ['sm', 'md', 'lg', 'xl', 'xxl']
        },
        {
            dataField: 'length', text: 'Length', sort: true, screenSizes: ['sm', 'md', 'lg', 'xl', 'xxl'],
            formatter: (cell) => `${cell} [m]`, align: 'right', headerAlign: 'right'
        },
        {
            dataField: 'beam', text: 'Beam', sort: true, screenSizes: ['sm', 'md', 'lg', 'xl', 'xxl'],
            align: 'right', headerAlign: 'right'
        },
        {
            dataField: 'bw', text: 'BW', sort: true, screenSizes: ['lg', 'xl', 'xxl'],
            align: 'right', headerAlign: 'right'
        },
        {
            dataField: 'nchan', text: 'Nchan', sort: true, screenSizes: ['lg', 'xl', 'xxl'],
            align: 'right', headerAlign: 'right'
        },
        { dataField: 'band', text: 'Band', sort: true, screenSizes: ['lg', 'xl', 'xxl'] },
        {
            dataField: 'nbin', text: 'Nbin', sort: true, screenSizes: ['lg', 'xl', 'xxl'],
            align: 'right', headerAlign: 'right'
        },
        {
            dataField: 'dmMeerpipe', text: 'DM psrcat', sort: true, screenSizes: ['xxl'],
            align: 'right', headerAlign: 'right'
        },
        {
            dataField: 'snMeerpipe', text: 'S/N raw', sort: true, screenSizes: ['xxl'],
            align: 'right', headerAlign: 'right'
        },
        {
            dataField: 'snBackend', text: 'S/N cleaned', sort: true, screenSizes: ['xxl'],
            align: 'right', headerAlign: 'right'
        },
        { dataField: 'action', text: '', sort: false, align: 'right', headerAlign: 'right', csvExport: false },
    ]
};

const trapum = {
    value: 'trapum',
    title: 'Trapum',
    subprojects: [
        'All'
    ],
    bandOptions: [
        'All',
        'L-BAND',
        'UHF',
        'S-BAND',
        'UNKNOWN'
    ]
};

const meertime = {
    value: 'meertime',
    title: 'MeerTime',
    subprojects: [
        'All',
        'TPA',
        'RelBin',
        'PTA',
        'GC',
        'NGC6440',
        'MeerTime',
        'Flux',
        'Unknown'
    ],
    bandOptions: [
        'All',
        'L-BAND',
        'UHF',
        'S-BAND',
        'UNKNOWN'
    ],
    columns: [
        { dataField: 'key', text: '', sort: false, hidden: true, toggle: false, csvExport: false },
        { dataField: 'plotLink', text: '', sort: false, hidden: true, toggle: false, csvExport: false },
        { dataField: 'utc', text: 'Timestamp', sort: true, headerClasses: 'fold-detail-utc' },
        {
            dataField: 'project', text: 'Project', sort: true,
            screenSizes: ['sm', 'md', 'lg', 'xl', 'xxl']
        },
        {
            dataField: 'length', text: 'Length', sort: true, screenSizes: ['sm', 'md', 'lg', 'xl', 'xxl'],
            formatter: (cell) => `${cell} [m]`, align: 'right', headerAlign: 'right'
        },
        {
            dataField: 'beam', text: 'Beam', sort: true, screenSizes: ['sm', 'md', 'lg', 'xl', 'xxl'],
            align: 'right', headerAlign: 'right'
        },
        {
            dataField: 'bw', text: 'BW', sort: true, screenSizes: ['lg', 'xl', 'xxl'],
            align: 'right', headerAlign: 'right'
        },
        {
            dataField: 'nchan', text: 'Nchan', sort: true, screenSizes: ['lg', 'xl', 'xxl'],
            align: 'right', headerAlign: 'right'
        },
        { dataField: 'band', text: 'Band', sort: true, screenSizes: ['lg', 'xl', 'xxl'] },
        {
            dataField: 'nbin', text: 'Nbin', sort: true, screenSizes: ['lg', 'xl', 'xxl'],
            align: 'right', headerAlign: 'right'
        },
        {
            dataField: 'nant', text: 'Nant', sort: true, screenSizes: ['lg', 'xl', 'xxl'],
            align: 'right', headerAlign: 'right'
        },
        {
            dataField: 'nantEff', text: 'Nant eff', sort: true, screenSizes: ['xl', 'xxl'],
            align: 'right', headerAlign: 'right'
        },
        {
            dataField: 'dmFold', text: 'DM fold', sort: true, screenSizes: ['xl', 'xxl'],
            align: 'right', headerAlign: 'right'
        },
        {
            dataField: 'dmMeerpipe', text: 'DM meerpipe', sort: true, screenSizes: ['xxl'],
            align: 'right', headerAlign: 'right'
        },
        {
            dataField: 'rmMeerpipe', text: 'RM meerpipe', sort: true, screenSizes: ['xxl'],
            align: 'right', headerAlign: 'right'
        },
        {
            dataField: 'snBackend', text: 'S/N backend', sort: true, screenSizes: ['xxl'],
            align: 'right', headerAlign: 'right'
        },
        {
            dataField: 'snMeerpipe', text: 'S/N meerpipe', sort: true, screenSizes: ['xxl'],
            align: 'right', headerAlign: 'right'
        },
        { dataField: 'action', text: '', sort: false, align: 'right', headerAlign: 'right', csvExport: false },
    ]
};

const allProjects = [meertime, trapum, molonglo];

const projectOptions = allProjects.map(
    project => <option value={project.value} key={project.value}>{project.title}</option>
);

export { molonglo, trapum, meertime, getProject, getSubProjectOptions, projectOptions };
