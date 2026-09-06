package com.mc.pgs.lab2.processor.service;

import com.mc.pgs.lab2.processor.domain.RefundOutcome;
import com.mc.pgs.lab2.processor.domain.RefundRecord;
import java.math.BigDecimal;

/**
 * The outcome of a refund decision, plus the order totals the response contract carries.
 *
 * <p>A business refusal is a structured result, not an exception: an expected outcome such as
 * "this exceeds the remaining refundable amount" is not an exceptional condition.
 */
public record RefundResult(
        RefundOutcome outcome,
        RefundRecord record,
        String reason,
        BigDecimal totalCapturedAmount,
        BigDecimal totalRefundedAmount) {
}
