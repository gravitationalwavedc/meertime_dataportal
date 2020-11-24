import logging
import database


GET_PTUSECONFIGS_ID_QUERY = """
SELECT id
FROM PTUSEConfigs
WHERE observation_id = %d and calibration_id = %d
LIMIT 1
"""

GET_PTUSECONFIGS_QUERY = """
SELECT observation_id, calibration_id, proposal_id, schedule_block_id, experiment_id, phaseup_id, delaycal_id, nant, nant_eff, configuration
FROM PTUSEConfigs
WHERE id = %d
LIMIT 1
"""

INSERT_PTUSECONFIGS_QUERY = """
INSERT INTO PTUSEConfigs (observation_id, calibration_id, proposal_id, schedule_block_id, experiment_id, phaseup_id, delaycal_id, nant, nant_eff, configuration)
VALUES (%d, %d, '%s', '%s', '%s', '%s', '%s', %d, %d, '%s')
"""


class PTUSEConfigs:
    def __init__(self, db):
        self.db = db

    def get_id(self, observation_id, calibration_id, hdr, create=False):
        """get the id for the pulsar from the hdr"""
        output = self._get_id(
            observation_id,
            calibration_id,
            hdr.proposal_id,
            hdr.schedule_block_id,
            hdr.experiment_id,
            hdr.phaseup_id,
            hdr.delaycal_id,
            hdr.nant,
            hdr.nant_eff,
            hdr.configuration,
        )
        if create and output is None:
            output = self.new(observation_id, calibration_id, hdr)
        return output

    def _get_id(
        self,
        observation_id,
        calibration_id,
        proposal_id,
        schedule_block_id,
        experiment_id,
        phaseup_id,
        delaycal_id,
        nant,
        nant_eff,
        configuration,
    ):
        """get the id for the specified instrument config"""
        query = GET_PTUSECONFIGS_ID_QUERY % (observation_id, calibration_id)
        try:
            output = self.db.get_singular_value(query, "id")
        except Exception as error:
            logging.error(str(error))
            raise error
        return output

    def get_ptuse_config(self, id):
        """get the ptuse config dict for specified id"""
        query = GET_PTUSECONFIGS_QUERY % (id)
        try:
            self.db.execute_query(query)
            return self.db.get_singular_value(query, "id")
        except Exception as error:
            logging.error(str(error))
            raise error
        output = self.db.get_output()
        if output is None:
            return None
        return database.util.singular_dict(output)

    def new(self, observation_id, calibration_id, hdr):
        return self._new(
            observation_id,
            calibration_id,
            hdr.proposal_id,
            hdr.schedule_block_id,
            hdr.experiment_id,
            hdr.phaseup_id,
            hdr.delaycal_id,
            hdr.nant,
            hdr.nant_eff,
            hdr.configuration,
        )

    def _new(
        self,
        observation_id,
        calibration_id,
        proposal_id,
        schedule_block_id,
        experiment_id,
        phaseup_id,
        delaycal_id,
        nant,
        nant_eff,
        configuration,
    ):
        query = INSERT_PTUSECONFIGS_QUERY % (
            observation_id,
            calibration_id,
            proposal_id,
            schedule_block_id,
            experiment_id,
            phaseup_id,
            delaycal_id,
            nant,
            nant_eff,
            configuration,
        )
        try:
            self.db.execute_insert(query)
        except Exception as error:
            logging.error(str(error))
            raise error
        return self.db.get_last_insert_id()
