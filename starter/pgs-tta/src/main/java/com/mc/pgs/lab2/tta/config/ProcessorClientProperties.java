package com.mc.pgs.lab2.tta.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

/**
 * Downstream connection details, externalised. No hostname or environment-specific URL is ever
 * written into source.
 */
@ConfigurationProperties(prefix = "processor")
public record ProcessorClientProperties(String baseUrl) {
}
