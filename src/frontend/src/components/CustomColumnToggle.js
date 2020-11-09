import React from 'react';
import { Dropdown, Button } from 'react-bootstrap';
import { HiDotsVertical, HiCheck } from 'react-icons/hi';


/* eslint react/display-name: 0 */

const CustomColumnToggle = ({ columns, onColumnToggle, toggles, exportCSVProps }) => {
    const CustomToggle = React.forwardRef(({ onClick }, ref) => (
        <Button
            ref={ref}
            onClick={(e) => {
                e.preventDefault();
                onClick(e);
            }}
            variant="icon"
            aria-label="table options"
            data-testid="tableOptions"
        >
            <HiDotsVertical className="h5"/>
        </Button>
    ));

    return (
        <Dropdown>
            <Dropdown.Toggle id="columnToggle" as={CustomToggle}/>
            <Dropdown.Menu>
                <Dropdown.Header>Download</Dropdown.Header>
                <Dropdown.Item onClick={() => exportCSVProps.onExport()}>Export as csv</Dropdown.Item>
                <Dropdown.Divider />
                <Dropdown.Header style={{ minWidth: '16rem' }}>Columns</Dropdown.Header>
                {
                    columns
                        .filter(column => column.dataField !== 'action')
                        .map(column => ({
                            ...column,
                            toggle: toggles[column.dataField]
                        }))
                        .map(column => (
                            <Dropdown.Item
                                key={ column.dataField }
                                aria-pressed={ column.toggle ? 'true' : 'false' }
                                onClick={() => onColumnToggle(column.dataField)}
                            >
                                { column.text } {column.toggle && 
                                  <HiCheck className="float-right"  data-testid="itemChecked"/>}
                            </Dropdown.Item>
                        ))
                }
            </Dropdown.Menu>
        </Dropdown>);
};

export default CustomColumnToggle;
