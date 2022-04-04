import { Button, Dropdown } from 'react-bootstrap';
import { HiCheck, HiCog } from 'react-icons/hi';

import React from 'react';

/* eslint react/display-name: 0 */

const CustomColumnToggle = ({ columns, onColumnToggle, toggles }) => {
    const CustomToggle = React.forwardRef(({ onClick }, ref) => (
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
            <HiCog className="icon"/>
            Columns 
        </Button>
    ));

    return (
        <Dropdown>
            <Dropdown.Toggle id="columnToggle" as={CustomToggle}/>
            <Dropdown.Menu>
                <Dropdown.Header style={{ minWidth: '16rem' }}>Columns</Dropdown.Header>
                {
                    columns
                        .filter(column => column.dataField !== 'action' && column.toggle !== false)
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
