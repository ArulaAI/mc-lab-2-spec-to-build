package com.mc.pgs.lab2.processor;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

import java.util.Map;

/**
 * Configuration lives in {@code pgs-payment-processor.yml} rather than {@code application.yml}.
 *
 * <p>Deployed on its own that distinction is invisible. It matters to the pair-verification
 * harness, which runs both services in one JVM: two {@code application.yml} files at the classpath
 * root do not merge, one silently wins, and the loser starts with the other service's
 * configuration. Naming each service's config after the service removes the collision entirely.
 */
@SpringBootApplication
public class PaymentProcessorApplication {

    public static final String CONFIG_NAME = "pgs-payment-processor";

    public static void main(String[] args) {
        SpringApplication app = new SpringApplication(PaymentProcessorApplication.class);
        app.setDefaultProperties(Map.of("spring.config.name", CONFIG_NAME));
        app.run(args);
    }
}
