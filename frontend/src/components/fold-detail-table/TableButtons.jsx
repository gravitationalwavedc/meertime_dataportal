import { Button, ButtonGroup } from "react-bootstrap";
import { Link } from "found";
import { formatDDMonYYYY } from "../../helpers";

const TableButtons = ({ row }) => {
  if (row.original.restricted) {
    const embargoEndDate = formatDDMonYYYY(row.original.embargoEndDate);
    return <span className="small">Embargoed until {embargoEndDate}</span>;
  }

  return (
    <ButtonGroup vertical>
      <Link
        to={row.original.viewLink}
        size="sm"
        variant="outline-secondary"
        as={Button}
      >
        View
      </Link>
      <Link
        to={row.original.sessionLink}
        size="sm"
        variant="outline-secondary"
        as={Button}
      >
        View session
      </Link>
    </ButtonGroup>
  );
};

export default TableButtons;
