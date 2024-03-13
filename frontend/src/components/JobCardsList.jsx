import JobCard from "./JobCard";
import React from "react";
import { handleSearch } from "../helpers";

const JobCardList = ({ data, columns, search, mainProject, as }) => {
  const results = search.searchText
    ? handleSearch(data, columns, search)
    : data;

  // Must be uppercase to use in JSX.
  const Component = as;

  console.log(results);

  return (
    <React.Fragment>
      {results.map((row) => (
        <Component
          key={row.key || row.jname}
          row={row}
          mainProject={mainProject}
        />
      ))}
    </React.Fragment>
  );
};

JobCardList.defaultProps = {
  as: JobCard,
};

export default JobCardList;
