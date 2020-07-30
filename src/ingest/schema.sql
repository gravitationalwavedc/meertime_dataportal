DROP TABLE `Pulsars`; DROP TABLE `UTCs`; DROP TABLE `Observations`; DROP TABLE `Proposals`;

CREATE TABLE `Pulsars` (
 `id` INT(11) NOT NULL AUTO_INCREMENT,
`Jname` text,
`state` text,
`GC` BOOL DEFAULT NULL,
`RelBin` BOOL DEFAULT NULL,
`TPA` BOOL DEFAULT NULL,
`PTA` BOOL DEFAULT NULL,
`comment` text,
PRIMARY KEY(`id`));

CREATE TABLE `UTCs` (
 `id` INT(11) NOT NULL AUTO_INCREMENT,
`utc` text,
`utc_ts` timestamp,
`annotation` text,
PRIMARY KEY(`id`)
);

# Keeping utc as an id because there can be multiple beams per utc.
CREATE TABLE `Observations` (
  `pulsar_id` int(11),
  `utc_id` int(11),
  `proposal_id` int(11) DEFAULT NULL,
  `beam` int(2),
  `comment` text,
  `length` double DEFAULT NULL,
  `bw` double DEFAULT NULL,
  `frequency` double DEFAULT NULL,
  `RM_pipe` double DEFAULT NULL,
  `DM_pipe` double DEFAULT NULL,
  `DM_fold` double DEFAULT NULL,
  `nchan` int(6) DEFAULT NULL,
  `nbin` int(5) DEFAULT NULL,
  `MJD` text,
  `MJD_INT` int(11) DEFAULT NULL,
  `MJD_frac` text,
  `PA` double DEFAULT NULL,
  `RA` text,
  `DEC` text,
  `observer` text,
  `SNR_pipe` double DEFAULT NULL,
  `SNR_spip` double DEFAULT NULL,
  `nant` int(3) DEFAULT NULL,
  `nant_eff` int(3) DEFAULT NULL,
  PRIMARY KEY (`pulsar_id`, `utc_id`, `beam`),
  FOREIGN KEY (`pulsar_id`) REFERENCES `Pulsars`(`id`),
  FOREIGN KEY (`utc_id`) REFERENCES `UTCs`(`id`)
);

CREATE TABLE `Fluxcal` (
  `pulsar_id` int(11),
  `utc_id` int(11),
  `proposal_id` int(11) DEFAULT NULL,
  `beam` int(2),
  `comment` text,
  `length` double DEFAULT NULL,
  `bw` double DEFAULT NULL,
  `frequency` double DEFAULT NULL,
  `nchan` int(6) DEFAULT NULL,
  `nbin` int(5) DEFAULT NULL,
  `MJD` text,
  `MJD_INT` int(11) DEFAULT NULL,
  `MJD_frac` text,
  `PA` double DEFAULT NULL,
  `RA` text,
  `DEC` text,
  `observer` text,
  `SNR_pipe` double DEFAULT NULL,
  `SNR_spip` double DEFAULT NULL,
  `nant` int(3) DEFAULT NULL,
  `nant_eff` int(3) DEFAULT NULL,
  PRIMARY KEY (`pulsar_id`, `utc_id`, `beam`),
  FOREIGN KEY (`pulsar_id`) REFERENCES `Pulsars`(`id`),
  FOREIGN KEY (`utc_id`) REFERENCES `UTCs`(`id`)
);

CREATE TABLE `Searchmode` (
  `pulsar_id` int(11),
  `utc_id` int(11),
  `proposal_id` int(11) DEFAULT NULL,
  `beam` int(2),
  `comment` text,
  `length` double DEFAULT NULL,
  `tsamp` double DEFAULT NULL,
  `bw` double DEFAULT NULL,
  `frequency` double DEFAULT NULL,
  `nchan` int DEFAULT NULL,
  `nbit` tinyint DEFAULT NULL,
  `npol` tinyint DEFAULT NULL,
  `nant` int DEFAULT NULL,
  `nant_eff` int DEFAULT NULL,
  `DM` double DEFAULT NULL,
  `RA` text,
  `DEC` text,
  PRIMARY KEY (`pulsar_id`, `utc_id`, `beam`),
  FOREIGN KEY (`pulsar_id`) REFERENCES `Pulsars`(`id`),
  FOREIGN KEY (`utc_id`) REFERENCES `UTCs`(`id`)
);


CREATE TABLE `Proposals` (
  `id` INT(3) NOT NULL AUTO_INCREMENT,
  `proposal` text,
  `proposal_short` text,
  PRIMARY KEY(`id`)
);
