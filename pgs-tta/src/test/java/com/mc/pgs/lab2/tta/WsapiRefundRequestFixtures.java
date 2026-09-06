package com.mc.pgs.lab2.tta;

import com.mc.pgs.lab2.tta.model.WsapiRefundRequest;

import java.math.BigDecimal;

/** Shared request fixtures. ORD-1 is the lab order carrying two captures totalling 150.00. */
public final class WsapiRefundRequestFixtures {

    private WsapiRefundRequestFixtures() {
    }

    public static WsapiRefundRequest paymentTargetRequest(String idempotencyKey, String amount) {
        return build(idempotencyKey, amount, null, false);
    }

    public static WsapiRefundRequest captureTargetRequest(String idempotencyKey, String amount) {
        return build(idempotencyKey, amount, "CT-9", false);
    }

    public static WsapiRefundRequest onlineRequest(String idempotencyKey, String amount) {
        return build(idempotencyKey, amount, null, true);
    }

    public static WsapiRefundRequest onlineCaptureTargetRequest(String idempotencyKey, String amount) {
        return build(idempotencyKey, amount, "CT-9", true);
    }

    public static WsapiRefundRequest build(String idempotencyKey, String amount,
                                           String targetTransactionId, boolean online) {
        return new WsapiRefundRequest(
                "MERCH-1", "TXN-1", "ORD-1", "62", idempotencyKey,
                new WsapiRefundRequest.TransactionDetails(
                        new BigDecimal(amount), "USD", "REF-1", targetTransactionId),
                new WsapiRefundRequest.ActionDetails(online));
    }
}
