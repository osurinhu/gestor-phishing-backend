CREATE TABLE `user` (
  `id` smallint NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `is_admin` tinyint(1) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `last_update` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
);

CREATE TABLE `group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `creator_id` smallint NOT NULL,
  `name` varchar(50) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `deleted` tinyint(1) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `last_update` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `creator_id` (`creator_id`),
  CONSTRAINT `group_ibfk_1` FOREIGN KEY (`creator_id`) REFERENCES `user` (`id`)
);

CREATE TABLE `target` (
  `id` int NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `creator_id` smallint NOT NULL,
  `name` varchar(50) NOT NULL,
  `person_code` varchar(25) NOT NULL,
  `email` varchar(255) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `last_update` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `group_id` (`group_id`),
  KEY `creator_id` (`creator_id`),
  CONSTRAINT `target_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `group` (`id`),
  CONSTRAINT `target_ibfk_2` FOREIGN KEY (`creator_id`) REFERENCES `user` (`id`)
);

CREATE TABLE `template` (
  `id` smallint NOT NULL AUTO_INCREMENT,
  `creator_id` smallint NOT NULL,
  `name` varchar(50) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `code` text NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `last_update` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `creator_id` (`creator_id`),
  CONSTRAINT `template_ibfk_1` FOREIGN KEY (`creator_id`) REFERENCES `user` (`id`)
);

CREATE TABLE `campaign` (
  `id` int NOT NULL AUTO_INCREMENT,
  `creator_id` smallint NOT NULL,
  `group_id` int NOT NULL,
  `template_id` smallint NOT NULL,
  `name` varchar(50) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `sender_email` varchar(255) NOT NULL,
  `status` varchar(1) NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `send_time` time NOT NULL,
  `subject_text` varchar(50) NOT NULL,
  `title_text` varchar(50) NOT NULL,
  `button_text` varchar(50) NOT NULL,
  `body_text` varchar(500) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `last_update` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `creator_id` (`creator_id`),
  KEY `group_id` (`group_id`),
  KEY `template_id` (`template_id`),
  CONSTRAINT `campaign_ibfk_1` FOREIGN KEY (`creator_id`) REFERENCES `user` (`id`),
  CONSTRAINT `campaign_ibfk_2` FOREIGN KEY (`group_id`) REFERENCES `group` (`id`),
  CONSTRAINT `campaign_ibfk_3` FOREIGN KEY (`template_id`) REFERENCES `template` (`id`)
);

CREATE TABLE `email_sent` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `target_id` int NOT NULL,
  `campaign_id` int NOT NULL,
  `interacted` tinyint(1) NOT NULL,
  `interaction_date` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `last_update` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `target_id` (`target_id`),
  KEY `campaign_id` (`campaign_id`),
  CONSTRAINT `email_sent_ibfk_1` FOREIGN KEY (`target_id`) REFERENCES `target` (`id`),
  CONSTRAINT `email_sent_ibfk_2` FOREIGN KEY (`campaign_id`) REFERENCES `campaign` (`id`)
);
