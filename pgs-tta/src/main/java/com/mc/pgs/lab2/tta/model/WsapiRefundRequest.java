package com.mc.pgs.lab2.tta.model;

import jakarta.validation.Valid;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.math.BigDecimal;

/**
 * The WSAPI-facing refund request as it arrives at TTA.
 *
 * <p>Constraints here are request-boundary validation: is this request structurally and
 * semantically acceptable for this interface? That is a different question from whether the
 * refund should be allowed, which depends on order state TTA does not hold.
 */
public record WsapiRefundRequest(
        @NotBlank String merchantId,
        @NotBlank String transactionId,
        @NotBlank String orderId,
        String version,

        /**
         * Retry identity supplied by the caller. Propagated across the seam unchanged; TTA never
         * derives, replaces or regenerates it (docs/PGS_DECISIONS.md 6.3, 6.4).
         */
        @NotBlank String idempotencyKey,

        @Valid @NotNull TransactionDetails transaction,
        @Valid ActionDetails action) {

    public record TransactionDetails(
            @NotNull @DecimalMin(value = "0.00", inclusive = false) BigDecimal amount,
            @NotBlank String currency,
            String reference,
            /** Present for the capture-target case; selects the capture-refund endpoint. */
            String targetTransactionId) {
    }

    public record ActionDetails(
            /** Online versus offline, supplied as an input to the seam. */
            Boolean refundAuthorization) {
    }

    public boolean isCaptureTargeted() {
        return transaction != null
                && transaction.targetTransactionId() != null
                && !transaction.targetTransactionId().isBlank();
    }

    public boolean isOnline() {
        return action != null && Boolean.TRUE.equals(action.refundAuthorization());
    }
}
