import _ from 'lodash';

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

