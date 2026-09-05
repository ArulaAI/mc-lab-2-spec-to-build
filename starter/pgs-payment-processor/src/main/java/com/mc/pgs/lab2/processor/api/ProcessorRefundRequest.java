package com.mc.pgs.lab2.processor.api;

import jakarta.validation.Valid;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.math.BigDecimal;

/**
 * The represented Payment Processor refund request.
 *
 * <p>Field names follow the source mapping table in {@code docs/PGS_DECISIONS.md} 2. Validation
 * here is this service's own boundary validation: every interface is a trust boundary, including
 * a call from another internal service, so nothing is taken on trust because TTA already checked.
 */
public record ProcessorRefundRequest(
        @NotBlank String merchantWsApiId,
        @Valid @NotNull WsApiSupport wsApiSupport,
        @Valid @NotNull Amounts amounts,
        @NotBlank String paymentCurrency,
        @Valid MerchantOrder merchantOrder) {

    public record WsApiSupport(
            @NotBlank String transactionWsApiId,
            @NotBlank String orderWsApiId,
            String wsApiVersion,
            String targetTransactionWsApiId,
            /**
             * Online versus offline, supplied as an input to the seam. Absent means offline,
             * which is what keeps an older consumer that never sends this field compatible.
             */
            Boolean refundAuthorization) {
    }

    public record Amounts(
            @NotNull @DecimalMin(value = "0.00", inclusive = false) BigDecimal transactionAmount) {
    }

    public record MerchantOrder(String transactionReference) {
    }
}
