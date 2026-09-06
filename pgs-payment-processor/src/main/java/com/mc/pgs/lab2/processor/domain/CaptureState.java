package com.mc.pgs.lab2.processor.domain;

import java.math.BigDecimal;

/**
 * One capture on an order.
 *
 * <p>Captures are individually refundable, and the source rule is per-capture as well as
 * per-order: "Per-capture refunds must not exceed each capture's amount"
 * ({@code docs/PGS_DECISIONS.md} 5.1). That is what makes the capture-refund endpoint
 * behaviourally different from the payment-refund endpoint rather than a routing preference.
 */
public record CaptureState(String captureTransactionId, BigDecimal amount) {
}
