CREATE TABLE `Observations` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `target_id` int NOT NULL,
  `utc_start` datetime NOT NULL,
  `duration` float NOT NULL,
  `obs_type` ENUM ('fold', 'search', 'baseband') NOT NULL,
  `telescope_id` int NOT NULL,
  `instrument_config_id` int NOT NULL,
  `suspect` bool NOT NULL,
  `comment` varchar(255)
);

CREATE TABLE `Telescopes` (
  `id` int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL
);

CREATE TABLE `InstrumentConfigs` (
  `id` int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `bandwidth` DECIMAL(12,6) NOT NULL,
  `frequency` DECIMAL(15,9) NOT NULL,
  `nchan` int NOT NULL,
  `npol` int NOT NULL,
  `beam` varchar(16) NOT NULL
);

CREATE TABLE `PTUSEConfigs` (
  `id` int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `observation_id` int NOT NULL,
  `calibration_id` int NOT NULL,
  `proposal_id` varchar(32) NOT NULL,
  `schedule_block_id` varchar(32) NOT NULL,
  `experiment_id` varchar(32) NOT NULL,
  `phaseup_id` varchar(32),
  `delaycal_id` varchar(32),
  `nant` int NOT NULL,
  `nant_eff` int NOT NULL,
  `configuration` JSON NOT NULL
);

CREATE TABLE `PTUSECalibrations` (
  `id` int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `calibration_type` ENUM ('pre', 'post', 'none') NOT NULL,
  `location` varchar(255)
);

CREATE TABLE `CASPSRConfigs` (
  `id` int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `observation_id` int NOT NULL,
  `pid` varchar(16) NOT NULL,
  `configuration` JSON NOT NULL
);

CREATE TABLE `Processings` (
  `id` int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `observation_id` int NOT NULL,
  `pipeline_id` int NOT NULL,
  `parent_id` int,
  `location` varchar(255) NOT NULL,
  `job_state` varchar(255),
  `job_output` JSON,
  `results` JSON
);

CREATE TABLE `Targets` (
  `id` int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `raj` varchar(16) NOT NULL,
  `decj` varchar(16) NOT NULL
);

CREATE TABLE `Pulsars` (
  `id` int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `jname` varchar(64) NOT NULL,
  `state` varchar(255),
  `comment` varchar(255)
);

CREATE TABLE `Pipelines` (
  `id` int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `description` varchar(255),
  `revision` varchar(16) NOT NULL,
  `created_at` datetime NOT NULL,
  `created_by` varchar(64) NOT NULL,
  `configuration` JSON
);

CREATE TABLE `Ephemerides` (
  `id` int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `pulsar_id` int NOT NULL,
  `created_at` datetime NOT NULL,
  `created_by` varchar(64) NOT NULL,
  `ephemeris` JSON NOT NULL,
  `p0` decimal(10,8) NOT NULL,
  `dm` float NOT NULL,
  `rm` float NOT NULL,
  `comment` varchar(255),
  `valid_from` datetime NOT NULL,
  `valid_to` datetime NOT NULL
);

CREATE TABLE `Basebandings` (
  `id` int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `processing_id` int NOT NULL
);

CREATE TABLE `Foldings` (
  `id` int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `processing_id` int NOT NULL,
  `folding_ephemeris_id` int NOT NULL,
  `nbin` int NOT NULL,
  `npol` int NOT NULL,
  `nchan` int NOT NULL,
  `dm` float,
  `tsubint` int NOT NULL
);

CREATE TABLE `Filterbankings` (
  `id` int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `processing_id` int NOT NULL,
  `nbit` int NOT NULL,
  `npol` int NOT NULL,
  `nchan` int NOT NULL,
  `tsamp` float NOT NULL,
  `dm` float NOT NULL
);

CREATE TABLE `PipelineImages` (
  `id` int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `processing_id` int NOT NULL,
  `rank` int NOT NULL,
  `image_type` varchar(64),
  `image` varchar(255) NOT NULL COMMENT 'The DJANGO image field'
);

CREATE TABLE `RFIs` (
  `id` int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `processing_id` int NOT NULL,
  `folding_id` int NOT NULL,
  `percent_zapped` float NOT NULL
);

CREATE TABLE `Toas` (
  `id` int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `processing_id` int NOT NULL,
  `input_folding_id` int NOT NULL,
  `timing_ephemeris_id` int,
  `template_id` int NOT NULL,
  `flags` JSON NOT NULL,
  `frequency` double NOT NULL,
  `mjd` varchar(32),
  `site` int,
  `uncertainty` float,
  `valid` bool,
  `comment` varchar(255)
);

CREATE TABLE `Templates` (
  `id` int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `pulsar_id` int NOT NULL,
  `frequency` float NOT NULL,
  `bandwidth` float NOT NULL,
  `created_at` datetime NOT NULL,
  `created_by` varchar(64) NOT NULL,
  `location` varchar(255) NOT NULL,
  `method` varchar(255),
  `type` varchar(255),
  `comment` varchar(255)
);

CREATE TABLE `Launches` (
  `pipeline_id` int NOT NULL,
  `parent_pipeline_id` int,
  `pulsar_id` int NOT NULL
);

CREATE TABLE `PulsarTargets` (
  `target_id` int NOT NULL,
  `pulsar_id` int NOT NULL
);

CREATE TABLE `PulsarAliases` (
  `pulsar_id` int NOT NULL,
  `alias` varchar(64) NOT NULL
);

CREATE TABLE `ProcessingCollections` (
  `processing_id` int NOT NULL,
  `collection_id` int NOT NULL
);

CREATE TABLE `Collections` (
  `id` int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `description` varchar(255)
);

ALTER TABLE `Observations` ADD FOREIGN KEY (`target_id`) REFERENCES `Targets` (`id`);

ALTER TABLE `Observations` ADD FOREIGN KEY (`telescope_id`) REFERENCES `Telescopes` (`id`);

ALTER TABLE `Observations` ADD FOREIGN KEY (`instrument_config_id`) REFERENCES `InstrumentConfigs` (`id`);

ALTER TABLE `PTUSEConfigs` ADD FOREIGN KEY (`observation_id`) REFERENCES `Observations` (`id`);

ALTER TABLE `PTUSEConfigs` ADD FOREIGN KEY (`calibration_id`) REFERENCES `PTUSECalibrations` (`id`);

ALTER TABLE `CASPSRConfigs` ADD FOREIGN KEY (`observation_id`) REFERENCES `Observations` (`id`);

ALTER TABLE `Processings` ADD FOREIGN KEY (`observation_id`) REFERENCES `Observations` (`id`);

ALTER TABLE `Processings` ADD FOREIGN KEY (`pipeline_id`) REFERENCES `Pipelines` (`id`);

ALTER TABLE `Processings` ADD FOREIGN KEY (`parent_id`) REFERENCES `Processings` (`id`);

ALTER TABLE `Ephemerides` ADD FOREIGN KEY (`pulsar_id`) REFERENCES `Pulsars` (`id`);

ALTER TABLE `Basebandings` ADD FOREIGN KEY (`processing_id`) REFERENCES `Processings` (`id`);

ALTER TABLE `Foldings` ADD FOREIGN KEY (`processing_id`) REFERENCES `Processings` (`id`);

ALTER TABLE `Foldings` ADD FOREIGN KEY (`folding_ephemeris_id`) REFERENCES `Ephemerides` (`id`);

ALTER TABLE `Filterbankings` ADD FOREIGN KEY (`processing_id`) REFERENCES `Processings` (`id`);

ALTER TABLE `PipelineImages` ADD FOREIGN KEY (`processing_id`) REFERENCES `Processings` (`id`);

ALTER TABLE `RFIs` ADD FOREIGN KEY (`processing_id`) REFERENCES `Processings` (`id`);

ALTER TABLE `RFIs` ADD FOREIGN KEY (`folding_id`) REFERENCES `Foldings` (`id`);

ALTER TABLE `Toas` ADD FOREIGN KEY (`processing_id`) REFERENCES `Processings` (`id`);

ALTER TABLE `Toas` ADD FOREIGN KEY (`input_folding_id`) REFERENCES `Foldings` (`id`);

ALTER TABLE `Toas` ADD FOREIGN KEY (`timing_ephemeris_id`) REFERENCES `Ephemerides` (`id`);

ALTER TABLE `Toas` ADD FOREIGN KEY (`template_id`) REFERENCES `Templates` (`id`);

ALTER TABLE `Templates` ADD FOREIGN KEY (`pulsar_id`) REFERENCES `Pulsars` (`id`);

ALTER TABLE `Launches` ADD FOREIGN KEY (`pipeline_id`) REFERENCES `Pipelines` (`id`);

ALTER TABLE `Launches` ADD FOREIGN KEY (`parent_pipeline_id`) REFERENCES `Pipelines` (`id`);

ALTER TABLE `Launches` ADD FOREIGN KEY (`pulsar_id`) REFERENCES `Pulsars` (`id`);

ALTER TABLE `PulsarTargets` ADD FOREIGN KEY (`target_id`) REFERENCES `Targets` (`id`);

ALTER TABLE `PulsarTargets` ADD FOREIGN KEY (`pulsar_id`) REFERENCES `Pulsars` (`id`);

ALTER TABLE `PulsarAliases` ADD FOREIGN KEY (`pulsar_id`) REFERENCES `Pulsars` (`id`);

ALTER TABLE `ProcessingCollections` ADD FOREIGN KEY (`processing_id`) REFERENCES `Processings` (`id`);

ALTER TABLE `ProcessingCollections` ADD FOREIGN KEY (`collection_id`) REFERENCES `Collections` (`id`);

ALTER TABLE `Observations` COMMENT = "Abstract definition of an observation - does not define the data product produced by PTUSE - that is performed in a Processings table entry";

ALTER TABLE `Telescopes` COMMENT = "common telescope configuration";

ALTER TABLE `InstrumentConfigs` COMMENT = "basic configuration of the telescope, the parameters are the input to the signal processing";

ALTER TABLE `PTUSEConfigs` COMMENT = "MeerKAT specific observation configuration parameters";

ALTER TABLE `CASPSRConfigs` COMMENT = "CASPSR specific observation configuration parameters";

ALTER TABLE `Processings` COMMENT = "Processing of an data from an observation, could include PTUSE search mode, PTUSE fold mode, OzStar fold of PTUSE search mode, RFI Cleaning of fold mode, etc";

ALTER TABLE `Targets` COMMENT = "antenna / tied array beam position";

ALTER TABLE `Pulsars` COMMENT = "both pulsars and calibrators in this table";

ALTER TABLE `Pipelines` COMMENT = "Definition of a processing pipeline including configuration parameters for that pipeline";

ALTER TABLE `Ephemerides` COMMENT = "copied from previous DB definition";

ALTER TABLE `Basebandings` COMMENT = "Processing that results in a baseband data product";

ALTER TABLE `Foldings` COMMENT = "Processing that results in a folded data product";

ALTER TABLE `Filterbankings` COMMENT = "Processing that results in a filterbank data product";

ALTER TABLE `PipelineImages` COMMENT = "Images produced by pipelines that will be uploaded to the webserver for display";

ALTER TABLE `RFIs` COMMENT = "RFI metrics from an observation, more detail could be added";

ALTER TABLE `Toas` COMMENT = "copied from previous DB definition";

ALTER TABLE `Templates` COMMENT = "copied from previous DB definition";

ALTER TABLE `Launches` COMMENT = "receipe for which pipelines should be run on which pulsars";

ALTER TABLE `PulsarTargets` COMMENT = "mapping from tied array beam target names to pulsar names - useful for GCs";

ALTER TABLE `PulsarAliases` COMMENT = "Alternate source names for the same pulsar";

ALTER TABLE `ProcessingCollections` COMMENT = "An mapping of processings to a collection";

ALTER TABLE `Collections` COMMENT = "An logical grouping which can host multple processings";
