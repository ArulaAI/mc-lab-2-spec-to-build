package com.mc.pgs.lab2.tta.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Checks a refund against the amount known to be captured on the order before sending it
 * downstream, so obviously excessive refunds are stopped early instead of making a round trip.
 */
@Component
public class LocalRefundLimitRule {

    private final BigDecimal knownCapturedAmount;
    private final Map<String, BigDecimal> refundedSoFar = new ConcurrentHashMap<>();

    public LocalRefundLimitRule(
            @Value("${processor.known-captured-amount:100.00}") BigDecimal knownCapturedAmount) {
        this.knownCapturedAmount = knownCapturedAmount;
    }

    public boolean exceedsRemaining(String orderId, BigDecimal amount) {
        BigDecimal used = refundedSoFar.getOrDefault(orderId, BigDecimal.ZERO);
        return amount.compareTo(knownCapturedAmount.subtract(used)) > 0;
    }

    public void recordRefunded(String orderId, BigDecimal amount) {
        refundedSoFar.merge(orderId, amount, BigDecimal::add);
    }
}
