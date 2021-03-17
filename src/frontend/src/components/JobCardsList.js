import JobCard from './JobCard';
import React from 'react';
import { handleSearch } from '../helpers';

const JobCardList = ({ data, columns, search, as }) => {
    
    const results = search.searchText ? handleSearch(data, columns, search) : data;

    // Must be uppercase to use in JSX.
    const Component = as;

    return (
        <React.Fragment>
            {results.map(row => <Component key={row.jname ? row.jname : row.key } row={row} />)}
        </React.Fragment>
    );
};

JobCardList.defaultProps = {
    as: JobCard
};

export default JobCardList;
