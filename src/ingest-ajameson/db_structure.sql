--
-- Produced using mysqldump from django-created db
--

--
-- Table structure for table `dataportal_basebandings`
--

DROP TABLE IF EXISTS `dataportal_basebandings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dataportal_basebandings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `processing_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `dataportal_basebandi_processing_id_cd5cd99d_fk_dataporta` (`processing_id`),
  CONSTRAINT `dataportal_basebandi_processing_id_cd5cd99d_fk_dataporta` FOREIGN KEY (`processing_id`) REFERENCES `dataportal_processings` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dataportal_calibrations`
--

DROP TABLE IF EXISTS `dataportal_calibrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dataportal_calibrations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `calibration_type` varchar(4) NOT NULL,
  `location` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dataportal_collections`
--

DROP TABLE IF EXISTS `dataportal_collections`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dataportal_collections` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dataportal_ephemerides`
--

DROP TABLE IF EXISTS `dataportal_ephemerides`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dataportal_ephemerides` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `created_by` varchar(64) NOT NULL,
  `ephemeris` longtext NOT NULL,
  `p0` decimal(10,8) NOT NULL,
  `dm` double NOT NULL,
  `rm` double NOT NULL,
  `comment` varchar(255) DEFAULT NULL,
  `valid_from` datetime(6) NOT NULL,
  `valid_to` datetime(6) NOT NULL,
  `pulsar_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `dataportal_ephemerid_pulsar_id_3e68759c_fk_dataporta` (`pulsar_id`),
  CONSTRAINT `dataportal_ephemerid_pulsar_id_3e68759c_fk_dataporta` FOREIGN KEY (`pulsar_id`) REFERENCES `dataportal_pulsars` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dataportal_filterbankings`
--

DROP TABLE IF EXISTS `dataportal_filterbankings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dataportal_filterbankings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nbit` int NOT NULL,
  `npol` int NOT NULL,
  `nchan` int NOT NULL,
  `tsamp` double NOT NULL,
  `dm` double NOT NULL,
  `processing_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `dataportal_filterban_processing_id_f1db930e_fk_dataporta` (`processing_id`),
  CONSTRAINT `dataportal_filterban_processing_id_f1db930e_fk_dataporta` FOREIGN KEY (`processing_id`) REFERENCES `dataportal_processings` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dataportal_foldings`
--

DROP TABLE IF EXISTS `dataportal_foldings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dataportal_foldings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nbin` int NOT NULL,
  `npol` int NOT NULL,
  `nchan` int NOT NULL,
  `dm` double DEFAULT NULL,
  `tsubint` int NOT NULL,
  `folding_ephemeris_id` int NOT NULL,
  `processing_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `dataportal_foldings_folding_ephemeris_id_28995ebf_fk_dataporta` (`folding_ephemeris_id`),
  KEY `dataportal_foldings_processing_id_1a5663e4_fk_dataporta` (`processing_id`),
  CONSTRAINT `dataportal_foldings_folding_ephemeris_id_28995ebf_fk_dataporta` FOREIGN KEY (`folding_ephemeris_id`) REFERENCES `dataportal_ephemerides` (`id`),
  CONSTRAINT `dataportal_foldings_processing_id_1a5663e4_fk_dataporta` FOREIGN KEY (`processing_id`) REFERENCES `dataportal_processings` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dataportal_instrumentconfigs`
--

DROP TABLE IF EXISTS `dataportal_instrumentconfigs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dataportal_instrumentconfigs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `bandwidth` decimal(12,6) NOT NULL,
  `frequency` decimal(15,9) NOT NULL,
  `nchan` int NOT NULL,
  `npol` int NOT NULL,
  `beam` varchar(16) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dataportal_launches`
--

DROP TABLE IF EXISTS `dataportal_launches`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dataportal_launches` (
  `id` int NOT NULL AUTO_INCREMENT,
  `parent_pipeline_id` int DEFAULT NULL,
  `pipeline_id` int NOT NULL,
  `pulsar_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `dataportal_launches_parent_pipeline_id_418735f2_fk_dataporta` (`parent_pipeline_id`),
  KEY `dataportal_launches_pipeline_id_06861798_fk_dataporta` (`pipeline_id`),
  KEY `dataportal_launches_pulsar_id_07ff17ce_fk_dataportal_pulsars_id` (`pulsar_id`),
  CONSTRAINT `dataportal_launches_parent_pipeline_id_418735f2_fk_dataporta` FOREIGN KEY (`parent_pipeline_id`) REFERENCES `dataportal_pipelines` (`id`),
  CONSTRAINT `dataportal_launches_pipeline_id_06861798_fk_dataporta` FOREIGN KEY (`pipeline_id`) REFERENCES `dataportal_pipelines` (`id`),
  CONSTRAINT `dataportal_launches_pulsar_id_07ff17ce_fk_dataportal_pulsars_id` FOREIGN KEY (`pulsar_id`) REFERENCES `dataportal_pulsars` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dataportal_observations`
--

DROP TABLE IF EXISTS `dataportal_observations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dataportal_observations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `config` json DEFAULT NULL,
  `utc_start` datetime(6) NOT NULL,
  `duration` double DEFAULT NULL,
  `nant` int DEFAULT NULL,
  `nant_eff` int DEFAULT NULL,
  `suspect` tinyint(1) NOT NULL,
  `comment` varchar(255) DEFAULT NULL,
  `calibration_id` int DEFAULT NULL,
  `instrument_config_id` int NOT NULL,
  `project_id` int NOT NULL,
  `target_id` int NOT NULL,
  `telescope_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `dataportal_observati_calibration_id_96ded406_fk_dataporta` (`calibration_id`),
  KEY `dataportal_observati_instrument_config_id_e1776b8c_fk_dataporta` (`instrument_config_id`),
  KEY `dataportal_observati_project_id_848e1e3d_fk_dataporta` (`project_id`),
  KEY `dataportal_observati_target_id_4c54834a_fk_dataporta` (`target_id`),
  KEY `dataportal_observati_telescope_id_8832a2ac_fk_dataporta` (`telescope_id`),
  CONSTRAINT `dataportal_observati_calibration_id_96ded406_fk_dataporta` FOREIGN KEY (`calibration_id`) REFERENCES `dataportal_calibrations` (`id`),
  CONSTRAINT `dataportal_observati_instrument_config_id_e1776b8c_fk_dataporta` FOREIGN KEY (`instrument_config_id`) REFERENCES `dataportal_instrumentconfigs` (`id`),
  CONSTRAINT `dataportal_observati_project_id_848e1e3d_fk_dataporta` FOREIGN KEY (`project_id`) REFERENCES `dataportal_projects` (`id`),
  CONSTRAINT `dataportal_observati_target_id_4c54834a_fk_dataporta` FOREIGN KEY (`target_id`) REFERENCES `dataportal_targets` (`id`),
  CONSTRAINT `dataportal_observati_telescope_id_8832a2ac_fk_dataporta` FOREIGN KEY (`telescope_id`) REFERENCES `dataportal_telescopes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dataportal_pipelineimages`
--

DROP TABLE IF EXISTS `dataportal_pipelineimages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dataportal_pipelineimages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `rank` int NOT NULL,
  `image_type` varchar(64) DEFAULT NULL,
  `image` varchar(255) NOT NULL,
  `processing_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `dataportal_pipelinei_processing_id_e60525d6_fk_dataporta` (`processing_id`),
  CONSTRAINT `dataportal_pipelinei_processing_id_e60525d6_fk_dataporta` FOREIGN KEY (`processing_id`) REFERENCES `dataportal_processings` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dataportal_pipelines`
--

DROP TABLE IF EXISTS `dataportal_pipelines`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dataportal_pipelines` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `revision` varchar(16) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `created_by` varchar(64) NOT NULL,
  `configuration` json DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dataportal_processingcollections`
--

DROP TABLE IF EXISTS `dataportal_processingcollections`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dataportal_processingcollections` (
  `id` int NOT NULL AUTO_INCREMENT,
  `collection_id` int NOT NULL,
  `processing_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `dataportal_processin_collection_id_1531a3ec_fk_dataporta` (`collection_id`),
  KEY `dataportal_processin_processing_id_11a1df46_fk_dataporta` (`processing_id`),
  CONSTRAINT `dataportal_processin_collection_id_1531a3ec_fk_dataporta` FOREIGN KEY (`collection_id`) REFERENCES `dataportal_collections` (`id`),
  CONSTRAINT `dataportal_processin_processing_id_11a1df46_fk_dataporta` FOREIGN KEY (`processing_id`) REFERENCES `dataportal_processings` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dataportal_processings`
--

DROP TABLE IF EXISTS `dataportal_processings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dataportal_processings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `embargo_end` datetime(6) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `location` varchar(255) NOT NULL,
  `job_state` varchar(255) DEFAULT NULL,
  `job_output` json DEFAULT NULL,
  `results` json DEFAULT NULL,
  `observation_id` int NOT NULL,
  `parent_id` int DEFAULT NULL,
  `pipeline_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `dataportal_processin_observation_id_b17374fa_fk_dataporta` (`observation_id`),
  KEY `dataportal_processin_parent_id_b8e9c97a_fk_dataporta` (`parent_id`),
  KEY `dataportal_processin_pipeline_id_a2b8120d_fk_dataporta` (`pipeline_id`),
  CONSTRAINT `dataportal_processin_observation_id_b17374fa_fk_dataporta` FOREIGN KEY (`observation_id`) REFERENCES `dataportal_observations` (`id`),
  CONSTRAINT `dataportal_processin_parent_id_b8e9c97a_fk_dataporta` FOREIGN KEY (`parent_id`) REFERENCES `dataportal_processings` (`id`),
  CONSTRAINT `dataportal_processin_pipeline_id_a2b8120d_fk_dataporta` FOREIGN KEY (`pipeline_id`) REFERENCES `dataportal_pipelines` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dataportal_projects`
--

DROP TABLE IF EXISTS `dataportal_projects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dataportal_projects` (
  `id` int NOT NULL AUTO_INCREMENT,
  `code` varchar(255) NOT NULL,
  `short` varchar(20) NOT NULL,
  `embargo_period` bigint NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dataportal_pulsaraliases`
--

DROP TABLE IF EXISTS `dataportal_pulsaraliases`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dataportal_pulsaraliases` (
  `id` int NOT NULL AUTO_INCREMENT,
  `alias` varchar(64) NOT NULL,
  `pulsar_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `dataportal_pulsarali_pulsar_id_90e08a20_fk_dataporta` (`pulsar_id`),
  CONSTRAINT `dataportal_pulsarali_pulsar_id_90e08a20_fk_dataporta` FOREIGN KEY (`pulsar_id`) REFERENCES `dataportal_pulsars` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dataportal_pulsars`
--

DROP TABLE IF EXISTS `dataportal_pulsars`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dataportal_pulsars` (
  `id` int NOT NULL AUTO_INCREMENT,
  `jname` varchar(64) NOT NULL,
  `state` varchar(255) DEFAULT NULL,
  `comment` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dataportal_pulsartargets`
--

DROP TABLE IF EXISTS `dataportal_pulsartargets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dataportal_pulsartargets` (
  `id` int NOT NULL AUTO_INCREMENT,
  `pulsar_id` int NOT NULL,
  `target_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `dataportal_pulsartar_pulsar_id_5ab05064_fk_dataporta` (`pulsar_id`),
  KEY `dataportal_pulsartar_target_id_fde4dabb_fk_dataporta` (`target_id`),
  CONSTRAINT `dataportal_pulsartar_pulsar_id_5ab05064_fk_dataporta` FOREIGN KEY (`pulsar_id`) REFERENCES `dataportal_pulsars` (`id`),
  CONSTRAINT `dataportal_pulsartar_target_id_fde4dabb_fk_dataporta` FOREIGN KEY (`target_id`) REFERENCES `dataportal_targets` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dataportal_rfis`
--

DROP TABLE IF EXISTS `dataportal_rfis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dataportal_rfis` (
  `id` int NOT NULL AUTO_INCREMENT,
  `percent_zapped` double NOT NULL,
  `folding_id` int NOT NULL,
  `processing_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `dataportal_rfis_folding_id_cd6b99fe_fk_dataportal_foldings_id` (`folding_id`),
  KEY `dataportal_rfis_processing_id_3d293796_fk_dataporta` (`processing_id`),
  CONSTRAINT `dataportal_rfis_folding_id_cd6b99fe_fk_dataportal_foldings_id` FOREIGN KEY (`folding_id`) REFERENCES `dataportal_foldings` (`id`),
  CONSTRAINT `dataportal_rfis_processing_id_3d293796_fk_dataporta` FOREIGN KEY (`processing_id`) REFERENCES `dataportal_processings` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dataportal_targets`
--

DROP TABLE IF EXISTS `dataportal_targets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dataportal_targets` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `raj` varchar(16) NOT NULL,
  `decj` varchar(16) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dataportal_telescopes`
--

DROP TABLE IF EXISTS `dataportal_telescopes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dataportal_telescopes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dataportal_templates`
--

DROP TABLE IF EXISTS `dataportal_templates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dataportal_templates` (
  `id` int NOT NULL AUTO_INCREMENT,
  `frequency` double NOT NULL,
  `bandwidth` double NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `created_by` varchar(64) NOT NULL,
  `location` varchar(255) NOT NULL,
  `method` varchar(255) DEFAULT NULL,
  `type` varchar(255) DEFAULT NULL,
  `comment` varchar(255) DEFAULT NULL,
  `pulsar_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `dataportal_templates_pulsar_id_120f5002_fk_dataportal_pulsars_id` (`pulsar_id`),
  CONSTRAINT `dataportal_templates_pulsar_id_120f5002_fk_dataportal_pulsars_id` FOREIGN KEY (`pulsar_id`) REFERENCES `dataportal_pulsars` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dataportal_toas`
--

DROP TABLE IF EXISTS `dataportal_toas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dataportal_toas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `flags` json NOT NULL,
  `frequency` double NOT NULL,
  `mjd` varchar(32) DEFAULT NULL,
  `site` int DEFAULT NULL,
  `uncertainty` double DEFAULT NULL,
  `quality` int DEFAULT NULL,
  `comment` varchar(255) DEFAULT NULL,
  `input_folding_id` int NOT NULL,
  `processing_id` int NOT NULL,
  `template_id` int NOT NULL,
  `timing_ephemeris_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `dataportal_toas_input_folding_id_eac98ced_fk_dataporta` (`input_folding_id`),
  KEY `dataportal_toas_processing_id_d2eb77e4_fk_dataporta` (`processing_id`),
  KEY `dataportal_toas_template_id_503d0842_fk_dataportal_templates_id` (`template_id`),
  KEY `dataportal_toas_timing_ephemeris_id_9a8830a3_fk_dataporta` (`timing_ephemeris_id`),
  CONSTRAINT `dataportal_toas_input_folding_id_eac98ced_fk_dataporta` FOREIGN KEY (`input_folding_id`) REFERENCES `dataportal_foldings` (`id`),
  CONSTRAINT `dataportal_toas_processing_id_d2eb77e4_fk_dataporta` FOREIGN KEY (`processing_id`) REFERENCES `dataportal_processings` (`id`),
  CONSTRAINT `dataportal_toas_template_id_503d0842_fk_dataportal_templates_id` FOREIGN KEY (`template_id`) REFERENCES `dataportal_templates` (`id`),
  CONSTRAINT `dataportal_toas_timing_ephemeris_id_9a8830a3_fk_dataporta` FOREIGN KEY (`timing_ephemeris_id`) REFERENCES `dataportal_ephemerides` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;