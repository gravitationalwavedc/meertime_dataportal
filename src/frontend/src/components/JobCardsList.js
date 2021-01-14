import JobCard from './JobCard';
import React from 'react';
import { handleSearch } from '../helpers';

const JobCardList = ({ data, columns, search }) => {
    
    const results = search.searchText ? handleSearch(data, columns, search) : data;

    return (
        <React.Fragment>
            {results.map(row => <JobCard key={row.jname ? row.jname : row.key } row={row} />)}
        </React.Fragment>
    );
};

export default JobCardList;
