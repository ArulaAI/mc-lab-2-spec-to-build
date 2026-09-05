package com.mc.pgs.lab2.processor.domain;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

/**
 * The stored order state this service holds and TTA does not.
 *
 * <p>{@code totalCapturedAmount} is the sum across every capture on the order. Because the
 * remaining-refundable determination depends on it, that determination is authoritative here.
 * See {@code docs/PGS_DECISIONS.md} 5.1 and 5.2.
 */
public record OrderState(String orderId, String currency, BigDecimal totalCapturedAmount,
                         List<CaptureState> captures) {

    public Optional<CaptureState> capture(String captureTransactionId) {
        if (captureTransactionId == null || captures == null) {
            return Optional.empty();
        }
        return captures.stream()
                .filter(c -> c.captureTransactionId().equals(captureTransactionId))
                .findFirst();
    }
}
