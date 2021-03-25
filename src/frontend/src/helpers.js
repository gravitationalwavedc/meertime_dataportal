import _ from 'lodash';
import moment from 'moment';

/* eslint-disable complexity */

export const handleSearch = (data, columns, search) => {
    // This search function mirrors the search done by standard BootsrapReactTable minus some of the features
    // that are only applicable to columns. 
    // It allows searching of any of the data values and doesn't care about letter case.
    const searchText = search.searchText.toLowerCase();

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

export const formatUTC = (utc) => moment.parseZone(utc, moment.ISO_8601).format('YYYY-MM-DD-HH:mm:ss');

export const kronosLink = (beam, jname, utc) => 
    `http://astronomy.swin.edu.au/pulsar/kronos/utc_start.php?beam=${beam}&utc_start=${utc}&jname=${jname}&data=${localStorage.meerWatchKey}`;

// This is a really insecure, temporary fix that will be changed asap.
export const meerWatchLink = (jname) =>
    `http://astronomy.swin.edu.au/pulsar/meerwatch/pulsar.php?jname=${jname}&data=${localStorage.meerWatchKey}`;

export const nullCellFormatter = cell => !cell ? '-' : cell;

export default { handleSearch, formatUTC, kronosLink, meerWatchLink, nullCellFormatter };
