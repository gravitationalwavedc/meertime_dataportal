import { forwardRef } from "react";
import { Button, Dropdown } from "react-bootstrap";
import { HiCheck, HiCog } from "react-icons/hi";

const CustomToggle = forwardRef(function CustomToggle({ onClick }, ref) {
  return (
    <Button
      ref={ref}
      onClick={(e) => {
        onClick(e);
      }}
      variant="link"
      size="sm"
      aria-label="table options"
      data-testid="tableOptions"
      className="mr-2 ml-2"
    >
      <HiCog className="icon" />
      Columns
    </Button>
  );
});

const CustomColumnToggle = ({ table }) => {
  console.log(table.getAllColumns());
  return (
    <Dropdown>
      <Dropdown.Toggle id="column-toggle" as={CustomToggle} />
      <Dropdown.Menu>
        <Dropdown.Header style={{ minWidth: "16rem" }}>Columns</Dropdown.Header>
        {table
          .getAllColumns()
          .filter((column) => column.getCanHide())
          .map((column) => (
            <Dropdown.Item
              key={column.id}
              onClick={column.getToggleVisibilityHandler()}
            >
              {column.columnDef.header}
              {column.getIsVisible() && (
                <HiCheck className="float-right" data-testid="itemChecked" />
              )}
            </Dropdown.Item>
          ))}
      </Dropdown.Menu>
    </Dropdown>
  );
};

export default CustomColumnToggle;
