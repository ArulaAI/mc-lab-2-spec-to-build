package com.mc.pgs.lab2.processor.service;

import com.mc.pgs.lab2.processor.domain.RefundMode;
import java.math.BigDecimal;

/**
 * A refund request reduced to the decisions this service must make. The idempotency identity
 * arrives from the caller and is used exactly as received: derivation is not modelled here.
 * See {@code docs/PGS_DECISIONS.md} 6.4.
 */
public record RefundCommand(
        String idempotencyKey,
        String cardPaymentGatewayId,
        String orderId,
        String targetTransactionId,
        BigDecimal amount,
        String currency,
        RefundMode mode) {
}
