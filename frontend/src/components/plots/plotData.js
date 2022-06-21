import { handleSearch } from '../../helpers';
import moment from 'moment';

export const snrPlotData = (data, columns, search) => {
    // Pass table data through the search filter to enable searching pulsars on chart.
    const results = search.searchText ? handleSearch(data, columns, search) : data;

    // Process the table data in a way that react-vis understands.
    const lBandData = results.filter(row => row.band === 'L-Band').map(row => ({ 
        time: moment(row.utc, 'YYYY-MM-DD-HH:mm:ss').valueOf(), 
        value: row.snMeerpipe ? row.snMeerpipe : row.snBackend,
        size: row.length, 
        link: row.plotLink
    }));

    const UHFData = results.filter(row => row.band === 'UHF').map(row => ({ 
        time: moment(row.utc, 'YYYY-MM-DD-HH:mm:ss').valueOf(), 
        value: row.snMeerpipe ? row.snMeerpipe : row.snBackend,
        size: row.length, 
        link: row.plotLink
    }));

    return { lBandData, UHFData };
};

export const fluxPlotData = (data, columns, search) => {
    // Pass table data through the search filter to enable searching pulsars on chart.
    const results = search.searchText ? handleSearch(data, columns, search) : data;
    console.log('HERE BE', search);

    // Process the table data in a way that react-vis understands.
    const lBandData = results.filter(row => row.band === 'L-Band').map(row => ({ 
        time: moment(row.utc, 'YYYY-MM-DD-HH:mm:ss').valueOf(), 
        value: row.flux,
        size: row.length,
        link: row.plotLink
    }));

    const UHFData = results.filter(row => row.band === 'UHF').map(row => ({ 
        time: moment(row.utc, 'YYYY-MM-DD-HH:mm:ss').valueOf(), 
        value: row.flux,
        size: row.length, 
        link: row.plotLink
    }));

    return { lBandData, UHFData };
};
