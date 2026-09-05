package com.mc.pgs.lab2.pair.support;

/** Request bodies used across the pair tests. ORD-1 carries two captures totalling 150.00. */
public final class RefundBodies {

    private RefundBodies() {
    }

    /** The WSAPI-facing shape TTA accepts. */
    public static String wsapi(String idempotencyKey, String amount, boolean online, String targetTransactionId) {
        String target = targetTransactionId == null ? "null" : "\"" + targetTransactionId + "\"";
        return """
               {
                 "merchantId": "MERCH-1",
                 "transactionId": "TXN-1",
                 "orderId": "ORD-1",
                 "version": "62",
                 "idempotencyKey": "%s",
                 "transaction": {
                   "amount": %s,
                   "currency": "USD",
                   "reference": "REF-1",
                   "targetTransactionId": %s
                 },
                 "action": { "refundAuthorization": %s }
               }
               """.formatted(idempotencyKey, amount, target, online);
    }

    /**
     * A contract-version-1 shaped body: no refundAuthorization field at all. This is what an
     * un-upgraded consumer sends.
     */
    public static String processorV1Shaped(String amount) {
        return """
               {
                 "merchantWsApiId": "MERCH-1",
                 "wsApiSupport": {
                   "transactionWsApiId": "TXN-1",
                   "orderWsApiId": "ORD-1",
                   "wsApiVersion": "62"
                 },
                 "amounts": { "transactionAmount": %s },
                 "paymentCurrency": "USD",
                 "merchantOrder": { "transactionReference": "REF-1" }
               }
               """.formatted(amount);
    }
}
