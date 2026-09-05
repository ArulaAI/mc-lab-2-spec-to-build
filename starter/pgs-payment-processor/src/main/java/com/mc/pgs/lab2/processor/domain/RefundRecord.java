package com.mc.pgs.lab2.processor.domain;

import java.math.BigDecimal;

/**
 * A recorded refund. The idempotency identity is the natural key: a repeated request carrying
 * the same identity must never produce a second record.
 */
public record RefundRecord(
        String idempotencyKey,
        String orderId,
        String targetTransactionId,
        BigDecimal amount,
        String currency,
        RefundMode mode,
        RefundOutcome outcome,
        String approvalCode) {

    public static RefundRecord approved(String idempotencyKey, String orderId, String targetTransactionId,
                                        BigDecimal amount, String currency, RefundMode mode,
                                        String approvalCode) {
        return new RefundRecord(idempotencyKey, orderId, targetTransactionId, amount, currency,
                mode, RefundOutcome.APPROVED, approvalCode);
    }
}
