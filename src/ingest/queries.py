# Pulsars
get_psr_id_q = "SELECT id FROM Pulsars WHERE Jname = %s"
insert_psr_q = "INSERT INTO Pulsars (Jname) VALUES (%s)"

# UTCs
get_utc_id_q = "SELECT id FROM UTCs WHERE utc = %s"
insert_utc_q = "INSERT INTO UTCs (`utc`, `utc_ts`) VALUES (%s, TIMESTAMP(%s))"

# Proposals
get_proposal_id_q = "SELECT id FROM Proposals WHERE proposal = %s"
insert_proposal_q = "INSERT INTO Proposals (`proposal`, `proposal_short`) VALUES (%s, %s)"

# Observations
# ignores SNR_spip and DM_fold
insert_obs_q = """
INSERT INTO Observations
(pulsar_id, utc_id,
length,
bw, frequency,
RM_pipe, DM_pipe,
nchan, nbin, nant, nant_eff,
MJD, MJD_INT, MJD_frac,
PA,
RA, `DEC`,
observer,
SNR_pipe)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

insert_update_processed_obs_q = """
INSERT INTO Observations
(pulsar_id, utc_id,
length,
bw, frequency,
RM_pipe, DM_pipe,
nchan, nbin, nant,
MJD, MJD_INT, MJD_frac,
PA,
RA, `DEC`,
observer,
SNR_pipe)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
length=%s,
bw=%s, frequency=%s,
RM_pipe=%s, DM_pipe=%s,
nchan=%s, nbin=%s, nant=%s,
MJD=%s, MJD_INT=%s, MJD_frac=%s,
PA=%s,
RA=%s, `DEC`=%s,
observer=%s,
SNR_pipe=%s
"""

insert_update_kronos_fluxcal_q = """
INSERT INTO Fluxcal
(pulsar_id, utc_id, proposal_id,
nchan, nbin, nant, nant_eff,
beam,
length, SNR_spip)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
beam=%s,
SNR_spip=%s,
proposal_id = %s, nant_eff = %s
"""

insert_update_kronos_fold_obs_q = """
INSERT INTO Observations
(pulsar_id, utc_id, proposal_id,
nchan, nbin, nant, nant_eff,
beam, DM_fold,
length, SNR_spip,
bw, frequency)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
beam=%s,
DM_fold=%s, SNR_spip=%s,
proposal_id = %s, nant_eff = %s,
length = %s,
bw = %s, frequency = %s
"""

insert_update_kronos_search_obs_q = """
INSERT INTO Searchmode
(`pulsar_id`, `utc_id`, `proposal_id`,
`nchan`, `nbit`, `npol`, `nant`, `nant_eff`,
`beam`, `DM`,
`bw`, `frequency`,
`length`, `tsamp`,
`RA`, `DEC`)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
length=%s, nant_eff = %s
"""

update_proposal = """
UPDATE Observations SET proposal_id = %s
WHERE pulsar_id = %s AND utc_id = %s AND beam = %s
"""

update_proposal_search = """
UPDATE Searchmode SET proposal_id = %s
WHERE pulsar_id = %s AND utc_id = %s AND beam = %s
"""

delete_from_obs_q = """
DELETE FROM Observations WHERE beam = %s AND utc_id = %s AND pulsar_id = %s
"""

delete_from_searchmode_q = """
DELETE FROM Searchmode WHERE beam = %s AND utc_id = %s AND pulsar_id = %s
"""

delete_from_fluxcal_q = """
DELETE FROM Fluxcal WHERE beam = %s AND utc_id = %s AND pulsar_id = %s
"""
