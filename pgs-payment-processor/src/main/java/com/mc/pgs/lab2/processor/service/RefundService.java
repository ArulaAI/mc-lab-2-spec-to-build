package com.mc.pgs.lab2.processor.service;

import com.mc.pgs.lab2.processor.client.RefundAuthorizationClient;
import com.mc.pgs.lab2.processor.domain.*;
import com.mc.pgs.lab2.processor.repo.OrderStateRepository;
import com.mc.pgs.lab2.processor.repo.RefundRecordRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.util.Optional;

/**
 * Owns the authoritative refund decisions represented in this lab slice.
 *
 * <p>Two of them depend on state only this service holds, which is what makes them
 * authoritative here and nowhere else:
 * <ul>
 *   <li>whether this refund duplicates one already accepted, judged on the propagated
 *       idempotency identity;</li>
 *   <li>whether the amount fits within the remaining refundable amount, judged on the order's
 *       total captured amount less what has already been refunded
 *       ({@code docs/PGS_DECISIONS.md} 5.1, 5.2).</li>
 * </ul>
 *
 * <p>This service never creates a settlement artifact. Settlement, injection, LCS and DCF are
 * downstream and outside this service ({@code docs/PGS_DECISIONS.md} 7.4).
 */
@Service
public class RefundService {

    private static final Logger log = LoggerFactory.getLogger(RefundService.class);

    private final RefundRecordRepository refunds;
    private final OrderStateRepository orders;
    private final RefundAuthorizationClient authorizationClient;

    public RefundService(RefundRecordRepository refunds,
                         OrderStateRepository orders,
                         RefundAuthorizationClient authorizationClient) {
        this.refunds = refunds;
        this.orders = orders;
        this.authorizationClient = authorizationClient;
    }

    public RefundResult refund(RefundCommand cmd) {
        // Duplicate detection comes first: a retry must not re-run any downstream effect.
        Optional<RefundRecord> existing = refunds.findByIdempotencyKey(cmd.idempotencyKey());
        if (existing.isPresent()) {
            RefundRecord prior = existing.get();
            log.info("Refund request is a duplicate of an existing refund for order {}", prior.orderId());
            return new RefundResult(RefundOutcome.DUPLICATE, prior,
                    "A refund already exists for this idempotency identity",
                    capturedFor(prior.orderId()), refunds.totalRefundedForOrder(prior.orderId()));
        }

        Optional<OrderState> order = orders.findByOrderId(cmd.orderId());
        if (order.isEmpty()) {
            return rejected(cmd, "No order state available for the supplied order", BigDecimal.ZERO, BigDecimal.ZERO);
        }

        BigDecimal totalCaptured = order.get().totalCapturedAmount();
        BigDecimal alreadyRefunded = refunds.totalRefundedForOrder(cmd.orderId());
        BigDecimal remaining = totalCaptured.subtract(alreadyRefunded);

        if (cmd.amount().compareTo(remaining) > 0) {
            // Source rule: a refund must not exceed the total captured amount. EXCESSIVE_REFUNDS
            // is not modelled in this slice (docs/PGS_DECISIONS.md 5.3).
            return rejected(cmd, "Refund amount exceeds the remaining refundable amount",
                    totalCaptured, alreadyRefunded);
        }

        // Per-capture rule: a refund targeting a specific capture must not exceed that capture's
        // own amount, which is a stricter bound than the order total. This is what makes the
        // capture-refund endpoint behaviourally different from the payment-refund endpoint.
        Optional<CaptureState> capture = order.get().capture(cmd.targetTransactionId());
        if (capture.isPresent()) {
            BigDecimal captureRemaining = capture.get().amount()
                    .subtract(refunds.totalRefundedForCapture(cmd.orderId(), cmd.targetTransactionId()));
            if (cmd.amount().compareTo(captureRemaining) > 0) {
                return rejected(cmd, "Refund amount exceeds the remaining amount on the targeted capture",
                        totalCaptured, alreadyRefunded);
            }
        }

        String approvalCode = null;
        if (cmd.mode() == RefundMode.ONLINE) {
            approvalCode = authorizationClient.authorize(cmd.orderId(), cmd.amount(), cmd.currency());
        }

        RefundRecord saved = refunds.save(RefundRecord.approved(
                cmd.idempotencyKey(), cmd.orderId(), cmd.targetTransactionId(),
                cmd.amount(), cmd.currency(), cmd.mode(), approvalCode));

        // Never log the approval code: an authorization code is sensitive data.
        log.info("Refund approved for order {} in {} mode", saved.orderId(), saved.mode());

        return new RefundResult(RefundOutcome.APPROVED, saved, null,
                totalCaptured, refunds.totalRefundedForOrder(cmd.orderId()));
    }

    private RefundResult rejected(RefundCommand cmd, String reason,
                                  BigDecimal totalCaptured, BigDecimal alreadyRefunded) {
        log.info("Refund rejected for order {}: {}", cmd.orderId(), reason);
        return new RefundResult(RefundOutcome.REJECTED, null, reason, totalCaptured, alreadyRefunded);
    }

    private BigDecimal capturedFor(String orderId) {
        return orders.findByOrderId(orderId)
                .map(OrderState::totalCapturedAmount)
                .orElse(BigDecimal.ZERO);
    }
}
