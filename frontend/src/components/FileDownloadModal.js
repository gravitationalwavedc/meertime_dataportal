import { Button, Modal, Table } from 'react-bootstrap';
import { createLink, formatProjectName } from '../helpers.js';
import React from 'react';

const FildDownloadModal = ({ visible, files, setShow }) => (
    <Modal
        show={visible}
        onHide={() => setShow(false)}
    >
        <Modal.Body>
            <h4 className="text-primary">
              Data files
            </h4>
            <Table>
                <thead>
                    <tr>
                        <th>Project</th>
                        <th>File Type</th>
                        <th>Size</th>
                        <th />
                    </tr>
                </thead>
                <tbody>
                    {files.edges.map((edge) =>
                        <tr key={edge.node.fileType}>
                            <td>{formatProjectName(edge.node.project)}</td>
                            <td>{edge.node.fileType}</td>
                            <td>{edge.node.size}</td>
                            <td>
                                <Button size="sm" variant="primary " onClick={() => createLink(edge.node.url)}
                                    disabled={edge.node.size === '0'}>
                                  Download
                                </Button>
                            </td>
                        </tr>
                    )}
                </tbody>
            </Table>
        </Modal.Body>
    </Modal>
);

export default FildDownloadModal;
