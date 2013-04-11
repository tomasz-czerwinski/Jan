BEGIN;
CREATE TABLE `Jan_strategy` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `strategy` integer NOT NULL,
    `description` varchar(250) NOT NULL
)
;
CREATE TABLE `Jan_branch` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `strategy_id` integer NOT NULL,
    `name` varchar(150) NOT NULL,
    `component` varchar(150) NOT NULL,
    `latest_delivered_revision` integer NOT NULL,
    `latest_fault_log_end` integer NOT NULL,
    `delivery_config` longtext NOT NULL,
    `svn_log_parser_config_patterns` varchar(300) NOT NULL,
    `svn_log_parser_config_relax_field` varchar(300) NOT NULL,
    `svn_log_parser_config_obligatory_patterns_map` varchar(300) NOT NULL,
    `svn_log_parser_config_allowed_patterns_states` varchar(300) NOT NULL,
    `cb_database_alias` varchar(150) NOT NULL,
    `cb_component_field_name` varchar(150) NOT NULL
)
;
ALTER TABLE `Jan_branch` ADD CONSTRAINT `strategy_id_refs_id_9e41cb48` FOREIGN KEY (`strategy_id`) REFERENCES `Jan_strategy` (`id`);
CREATE TABLE `Jan_deliverylocation` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `branch_id` integer NOT NULL,
    `to_location` varchar(150) NOT NULL
)
;
ALTER TABLE `Jan_deliverylocation` ADD CONSTRAINT `branch_id_refs_id_cc81e7c0` FOREIGN KEY (`branch_id`) REFERENCES `Jan_branch` (`id`);
CREATE TABLE `Jan_content` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `content` longtext NOT NULL,
    `location` varchar(150) NOT NULL,
    `revision` integer NOT NULL,
    `content_note_link` varchar(150) NOT NULL,
    `name` varchar(150) NOT NULL,
    `system` varchar(150) NOT NULL,
    `fault_log_location` varchar(300) NOT NULL,
    `fault_log_start` integer NOT NULL,
    `fault_log_end` integer NOT NULL,
    `compilation_date` datetime NOT NULL,
    `parsed` bool NOT NULL
)
;
CREATE TABLE `Jan_fault` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `content_id` integer NOT NULL,
    `pronto` varchar(150) NOT NULL,
    `revision` integer NOT NULL,
    `info` varchar(150) NOT NULL,
    `partial` bool NOT NULL,
    `description` varchar(400) NOT NULL,
    `module` varchar(150) NOT NULL
)
;
ALTER TABLE `Jan_fault` ADD CONSTRAINT `content_id_refs_id_1fbca632` FOREIGN KEY (`content_id`) REFERENCES `Jan_content` (`id`);
CREATE TABLE `Jan_baseline` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `content_id` integer NOT NULL,
    `baseline` varchar(250) NOT NULL
)
;
ALTER TABLE `Jan_baseline` ADD CONSTRAINT `content_id_refs_id_20ce7d12` FOREIGN KEY (`content_id`) REFERENCES `Jan_content` (`id`);
CREATE TABLE `Jan_external` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `content_id` integer NOT NULL,
    `external` varchar(250) NOT NULL
)
;
ALTER TABLE `Jan_external` ADD CONSTRAINT `content_id_refs_id_ecbd42ca` FOREIGN KEY (`content_id`) REFERENCES `Jan_content` (`id`);
CREATE TABLE `Jan_build` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `branch_id` integer NOT NULL,
    `content_id` integer NOT NULL
)
;
ALTER TABLE `Jan_build` ADD CONSTRAINT `content_id_refs_id_74ed44fe` FOREIGN KEY (`content_id`) REFERENCES `Jan_content` (`id`);
ALTER TABLE `Jan_build` ADD CONSTRAINT `branch_id_refs_id_c6ca2150` FOREIGN KEY (`branch_id`) REFERENCES `Jan_branch` (`id`);
CREATE TABLE `Jan_queue` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `build_id` integer NOT NULL,
    `place` integer NOT NULL,
    `release_date` datetime NOT NULL,
    `from_location` varchar(150) NOT NULL
)
;
ALTER TABLE `Jan_queue` ADD CONSTRAINT `build_id_refs_id_64374fac` FOREIGN KEY (`build_id`) REFERENCES `Jan_build` (`id`);
CREATE TABLE `Jan_history` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `build_id` integer NOT NULL,
    `place` integer NOT NULL,
    `release_date` datetime NOT NULL,
    `from_location` varchar(150) NOT NULL
)
;
ALTER TABLE `Jan_history` ADD CONSTRAINT `build_id_refs_id_7681f833` FOREIGN KEY (`build_id`) REFERENCES `Jan_build` (`id`);
CREATE TABLE `Jan_historydeliverylocation` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `history_id` integer NOT NULL,
    `to_location` varchar(150) NOT NULL
)
;
ALTER TABLE `Jan_historydeliverylocation` ADD CONSTRAINT `history_id_refs_id_1114735c` FOREIGN KEY (`history_id`) REFERENCES `Jan_history` (`id`);
CREATE TABLE `Jan_historyfault` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `content_id` integer NOT NULL,
    `pronto` varchar(150) NOT NULL,
    `revision` integer NOT NULL,
    `info` varchar(150) NOT NULL,
    `partial` bool NOT NULL,
    `description` varchar(400) NOT NULL,
    `module` varchar(150) NOT NULL
)
;
ALTER TABLE `Jan_historyfault` ADD CONSTRAINT `content_id_refs_id_d4812451` FOREIGN KEY (`content_id`) REFERENCES `Jan_content` (`id`);
CREATE INDEX `Jan_branch_d96ed8f` ON `Jan_branch` (`strategy_id`);
CREATE INDEX `Jan_deliverylocation_d56253ba` ON `Jan_deliverylocation` (`branch_id`);
CREATE INDEX `Jan_fault_cc8ff3c` ON `Jan_fault` (`content_id`);
CREATE INDEX `Jan_baseline_cc8ff3c` ON `Jan_baseline` (`content_id`);
CREATE INDEX `Jan_external_cc8ff3c` ON `Jan_external` (`content_id`);
CREATE INDEX `Jan_build_d56253ba` ON `Jan_build` (`branch_id`);
CREATE INDEX `Jan_build_cc8ff3c` ON `Jan_build` (`content_id`);
CREATE INDEX `Jan_queue_f0e09603` ON `Jan_queue` (`build_id`);
CREATE INDEX `Jan_history_f0e09603` ON `Jan_history` (`build_id`);
CREATE INDEX `Jan_historydeliverylocation_6c9c0cef` ON `Jan_historydeliverylocation` (`history_id`);
CREATE INDEX `Jan_historyfault_cc8ff3c` ON `Jan_historyfault` (`content_id`);
COMMIT;
