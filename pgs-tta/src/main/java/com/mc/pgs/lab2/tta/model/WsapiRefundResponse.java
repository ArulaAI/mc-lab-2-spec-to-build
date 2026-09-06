package com.mc.pgs.lab2.tta.model;

import java.math.BigDecimal;

/** The caller-facing refund response TTA returns. */
public record WsapiRefundResponse(Order order, Transaction transaction) {

    public record Order(BigDecimal totalCapturedAmount, BigDecimal totalRefundedAmount, String status) {
    }

    public record Transaction(String responseCode, String approvalCode) {
    }
}
