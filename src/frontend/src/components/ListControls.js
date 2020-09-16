import React from 'react';
import Form from 'react-bootstrap/Form';
import Col from 'react-bootstrap/Col';

const ListControls = () => 
      <Form>
        <Form.Row>
          <Col>
            <Form.Group controlId="projectSelect">
              <Form.Label>Select project</Form.Label>
              <Form.Control as="select">
                <option>All projects</option>
              </Form.Control>
            </Form.Group>
          </Col>
          <Col>
            <Form.Group controlId="jobSearch">
              <Form.Label>Search</Form.Label>
              <Form.Control></Form.Control>
            </Form.Group>
          </Col>
        </Form.Row>
      </Form>;

export default ListControls;
