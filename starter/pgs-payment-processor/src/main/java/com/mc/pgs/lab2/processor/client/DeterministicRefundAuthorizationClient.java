package com.mc.pgs.lab2.processor.client;

import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.util.Locale;

/**
 * Deterministic lab stub. Same inputs always produce the same approval code, and nothing leaves
 * the process. Never logs the approval code it produces: an authorization code is sensitive.
 */
@Component
public class DeterministicRefundAuthorizationClient implements RefundAuthorizationClient {

    @Override
    public String authorize(String orderId, BigDecimal amount, String currency) {
        int hash = (orderId + "|" + amount.stripTrailingZeros().toPlainString() + "|" + currency).hashCode();
        return String.format(Locale.ROOT, "APR%06X", hash & 0xFFFFFF);
    }
}
