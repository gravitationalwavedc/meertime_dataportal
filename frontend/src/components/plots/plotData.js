import { handleSearch, scaleValue } from '../../helpers';
import moment from 'moment';

export const pulsarSummaryPlotData = (
    data, 
    columns, 
    search, 
    lastDrawLocation, 
    setLastDrawLocation, 
    maxPlotLength) => {
    // Pass table data through the search filter to enable searching pulsars on chart.
    const results = search.searchText ? handleSearch(data, columns, search) : data;

    // Process the table data in a way that react-vis understands.
    const plotData = results.map(row => ({ 
        x: moment(row.utc, 'YYYY-MM-DD-HH:mm:ss'), 
        y: row.snMeerpipe ? row.snMeerpipe : row.snBackend,
        value: row.snMeerpipe ? row.snMeerpipe : row.snBackend,
        type: row.snMeerpipe ? 'Meerpipe S/N' : 'raw S/N',
        customComponent: row.band.toLowerCase() === 'l-band' ? 'square' : 'circle',
        style: { fill:'#E07761', opacity:'0.7' },
        size: scaleValue(Math.log(row.length), [0, Math.log(maxPlotLength)], [1, 100]),
        color: '#E07761',
        length: row.length,
        link: row.plotLink
    }));

    if (plotData.length && plotData.length < 2 && lastDrawLocation === null){
        setLastDrawLocation({
            top: plotData[0].y + 100,
            bottom: plotData[0].y - 100,
            left: plotData[0].x.clone().subtract(3, 'days').toDate(), 
            right: plotData[0].x.clone().add(3, 'days').toDate()
        });
    }

    return plotData;
};

export const fluxPlotData = (
    data, 
    columns, 
    search, 
    lastDrawLocation, 
    setLastDrawLocation, 
    maxPlotLength) => {
    // Pass table data through the search filter to enable searching pulsars on chart.
    const results = search.searchText ? handleSearch(data, columns, search) : data;

    // Process the table data in a way that react-vis understands.
    const plotData = results.map(row => ({ 
        x: moment(row.utc, 'YYYY-MM-DD-HH:mm:ss'), 
        y: row.flux,
        value: row.flux,
        customComponent: row.band.toLowerCase() === 'l-band' ? 'square' : 'circle',
        style: { fill:'#E07761', opacity:'0.7' },
        size: scaleValue(Math.log(row.length), [0, Math.log(maxPlotLength)], [1, 100]),
        color: '#E07761',
        length: row.length,
        link: row.plotLink
    }));

    if (plotData.length && plotData.length < 2 && lastDrawLocation === null){
        setLastDrawLocation({
            top: plotData[0].y + 100,
            bottom: plotData[0].y - 100,
            left: plotData[0].x.clone().subtract(3, 'days').toDate(), 
            right: plotData[0].x.clone().add(3, 'days').toDate()
        });
    }

    return plotData;
};

export default {
    pulsarSummaryPlotData,
    fluxPlotData
};
