import { ButtonGroup, Dropdown, DropdownButton } from 'react-bootstrap';

import React from 'react';

const CustomSizePerPageBtn = ({
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

export default CustomSizePerPageBtn;
