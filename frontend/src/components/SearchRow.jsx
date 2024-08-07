import { HiDownload, HiViewGrid, HiViewList } from "react-icons/hi";

import Button from "react-bootstrap/Button";
import Col from "react-bootstrap/Col";
import CustomColumnToggle from "./CustomColumnToggle";
import Form from "react-bootstrap/Form";
import SearchBar from "./SearchBar";
import ToggleButton from "react-bootstrap/ToggleButton";
import ToggleButtonGroup from "react-bootstrap/ToggleButtonGroup";

const SearchRow = ({
  setIsTableView,
  isTableView,
  searchText,
  searchProps,
  columnToggleProps,
  exportCSVProps,
  query,
  rememberSearch,
}) => (
  <Form.Row className="searchbar">
    <Col xl={3} md={4}>
      <Form.Group controlId="jobSearch">
        <Form.Label>Search</Form.Label>
        <SearchBar
          label="Search"
          placeholder={searchText}
          query={query}
          {...searchProps}
          rememberSearch={rememberSearch}
        />
      </Form.Group>
    </Col>
    <Form.Group>
      <ToggleButtonGroup
        className="ml-2"
        type="radio"
        name="viewType"
        defaultValue={isTableView ? "table" : "list"}
      >
        <ToggleButton
          data-testid="table-view-button"
          variant="outline-primary"
          size="sm"
          value="table"
          onClick={() => setIsTableView(true)}
        >
          <HiViewGrid className="icon" />
          Table view
        </ToggleButton>
        <ToggleButton
          data-testid="list-view-button"
          variant="outline-primary"
          value="list"
          size="sm"
          onClick={() => setIsTableView(false)}
        >
          <HiViewList className="icon" />
          List view
        </ToggleButton>
      </ToggleButtonGroup>
    </Form.Group>
    {isTableView && <CustomColumnToggle {...columnToggleProps} />}
    {isTableView && (
      <Form.Group>
        <Button
          variant="link"
          size="sm"
          onClick={() => exportCSVProps.onExport()}
        >
          <HiDownload className="icon" />
          Download CSV
        </Button>
      </Form.Group>
    )}
  </Form.Row>
);

SearchRow.defaultProps = {
  query: null,
  rememberSearch: false,
};

export default SearchRow;
