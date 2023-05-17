import { Modal, Table } from 'react-bootstrap';
import React from 'react';

const FildDownloadModal = ({ visible, files, setShow }) => {
    console.log(files.edges);
    return (
        <Modal
            show={visible}
            onHide={() => setShow(false)}
        >
            <Modal.Header>
                <Modal.Title className="text-primary">Download a file</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <Table>
                    <tbody>
                        {files.edges.map((edge) =>
                            <tr key={edge.node.fileType}>
                                <th>Project</th>
                                <td>{edge.node.project}</td>
                                <td>{edge.node.fileType}</td>
                                <td>{edge.node.url}</td>
                            </tr>
                        )}
                    </tbody>
                </Table>
            </Modal.Body>
        </Modal>
    );
};

export default FildDownloadModal;
