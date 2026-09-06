package com.mc.pgs.lab2.processor.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

import java.math.BigDecimal;
import java.util.List;

/**
 * Externalised lab fixture data. The seeded orders live in configuration rather than in source so
 * the fixture is visible and changeable without editing code.
 */
@ConfigurationProperties(prefix = "lab.refund")
public record RefundProperties(List<SeededOrder> orders) {

    public record SeededOrder(String orderId, String currency, BigDecimal totalCapturedAmount,
                              List<SeededCapture> captures) {
    }

    public record SeededCapture(String captureTransactionId, BigDecimal amount) {
    }
}
