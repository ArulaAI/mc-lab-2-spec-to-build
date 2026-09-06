package com.mc.pgs.lab2.processor.api;

import java.math.BigDecimal;

/**
 * The represented refund response. Field selection follows {@code docs/PGS_DECISIONS.md} 1.2.
 */
public record ProcessorRefundResponse(Order order, Transaction transaction) {

    public record Order(BigDecimal totalCapturedAmount, BigDecimal totalRefundedAmount, String status) {
    }

    public record Transaction(AuthorizationResponse authorizationResponse) {
    }

    public record AuthorizationResponse(String responseCode, String approvalCode) {
    }
}
