import React from 'react';
import { ButtonGroup, DropdownButton, Dropdown } from 'react-bootstrap';

const sizePerPageRenderer = ({
    options,
    currSizePerPage,
    onSizePerPageChange
}) => (

    <ButtonGroup className="mr-3">
        <DropdownButton variant="primary" size="sm" id="page-select" title={currSizePerPage}>
            {
                options.map(option => (
                    <Dropdown.Item
                        key={ option.text }
                        as="button"
                        onClick={ () => onSizePerPageChange(option.page) }
                    >
                        { option.text } per page
                    </Dropdown.Item>
                ))
            }
        </DropdownButton>
    </ButtonGroup>
);

export default sizePerPageRenderer;
