package com.mc.pgs.lab2.tta;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;

import java.util.Map;

/**
 * Configuration lives in {@code pgs-tta.yml} rather than {@code application.yml}. See
 * {@code PaymentProcessorApplication} for why: two services sharing a JVM must not share a
 * config file name.
 */
@SpringBootApplication
@ConfigurationPropertiesScan
public class TtaApplication {

    public static final String CONFIG_NAME = "pgs-tta";

    public static void main(String[] args) {
        SpringApplication app = new SpringApplication(TtaApplication.class);
        app.setDefaultProperties(Map.of("spring.config.name", CONFIG_NAME));
        app.run(args);
    }
}
