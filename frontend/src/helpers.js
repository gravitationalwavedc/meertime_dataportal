import _ from 'lodash';
import moment from 'moment';

/* eslint-disable complexity */

export const handleSearch = (data, columns, search) => {
    // This search function mirrors the search done by standard BootsrapReactTable minus some of the features
    // that are only applicable to columns. 
    // It allows searching of any of the data values and doesn't care about letter case.
    const searchText = search.searchText ? search.searchText.toLowerCase() : '';

    return data.filter((row) => {
        for (let columnIndex = 0; columnIndex < columns.length; columnIndex += 1) {
            const column = columns[columnIndex];

            if (column.searchable === false) continue;

            let targetValue = _.get(row, column.dataField);

            if (targetValue !== null && typeof targetValue !== 'undefined') {
                targetValue = targetValue.toString().toLowerCase();
                if (targetValue.indexOf(searchText) > -1) {
                    return true;
                }
            }
        }
        return false;
    });
};

export const formatDDMonYYYY = (utc) => moment.parseZone(utc, moment.ISO_8601).format('DD MMM YYYY');

export const formatUTC = (utc) => moment.parseZone(utc, moment.ISO_8601).format('YYYY-MM-DD-HH:mm:ss');

export const kronosLink = (beam, jname, utc) =>
    `http://astronomy.swin.edu.au/pulsar/kronos/utc_start.php?beam=${beam}&utc_start=${utc}&jname=${jname}&data=${localStorage.meerWatchKey}`;

// This is a really insecure, temporary fix that will be changed asap.
export const meerWatchLink = (jname) =>
    `http://astronomy.swin.edu.au/pulsar/meerwatch/pulsar.php?jname=${jname}&data=${localStorage.meerWatchKey}`;

export const nullCellFormatter = cell => !cell ? '-' : cell;

export const columnsSizeFilter = (columns, screenSize) => {

    columns.filter(column => ('screenSizes' in column) && !column.screenSizes.includes(screenSize))
        .map(column => column['hidden'] = true);

    return columns;
};

export const scaleValue = (value, from, to) => {

    const scale = (to[1] - to[0]) / (from[1] - from[0]);
    const capped = Math.min(from[1], Math.max(from[0], value)) - from[0];

    return ~~(capped * scale + to[0]);
};

export const formatProjectName = (projectName) => {
    if(!projectName) return null;    

    const projectDisplayNames = {
        relbin: 'RelBin',
        gc: 'GC',
        pta: 'PTA',
        tpa: 'TPA',
        phaseups: 'Phaseups',
        ngc6440: 'NGC6440',
        unknown: 'Unknown',
        meertime: 'MeerTime',
        flux: 'Flux'
    };

    if (projectName.toLowerCase() in projectDisplayNames) {
        return projectDisplayNames[projectName.toLowerCase()];
    }

    return projectName;
};

export const formatSingleObservationData = (data) => {

    const excludeTitles = [
        'jname',
        'beam',
        'utc'
    ];

    const displayTitles = {
        proposal: 'Proposal',
        project: 'Project',
        length: 'Length',
        nbin: 'Nbin',
        nchan: 'Nchan',
        frequency: 'Frequency (MHz)',
        bw: 'Bandwidth (MHz)',
        ra: 'RA',
        dec: 'DEC',
        tsubint: 'Subint Time (s)',
        nant: 'Number of Antennas'
    };

    const dataItems = Object.keys(data)
        .filter(key => !excludeTitles.includes(key) && key !== 'images')
        .reduce((result, key) => ({ ...result, [displayTitles[key]]: data[key] }), {});

    return dataItems;
};

export default {
    columnsSizeFilter,
    handleSearch,
    formatUTC,
    kronosLink,
    meerWatchLink,
    nullCellFormatter,
    scaleValue,
    formatProjectName,
    formatSingleObservationData
};


