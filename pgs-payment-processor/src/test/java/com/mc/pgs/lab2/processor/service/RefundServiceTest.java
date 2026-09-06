package com.mc.pgs.lab2.processor.service;

import com.mc.pgs.lab2.processor.client.RecordingRefundAuthorizationClient;
import com.mc.pgs.lab2.processor.domain.*;
import com.mc.pgs.lab2.processor.repo.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Payment Processor owns the authoritative refund decisions represented in this lab slice.
 *
 * <p>Order ORD-1 is the lab fixture: two captures, C1 = 100.00 and C2 = 50.00, so the total
 * captured amount is 150.00. That total is state only this service holds, which is why the
 * remaining-refundable determination is authoritative here and nowhere else.
 */
class RefundServiceTest {

    private InMemoryRefundRecordRepository refunds;
    private RecordingRefundAuthorizationClient authClient;
    private RefundService service;

    @BeforeEach
    void setUp() {
        refunds = new InMemoryRefundRecordRepository();
        OrderStateRepository orders = new InMemoryOrderStateRepository(List.of(
                new OrderState("ORD-1", "USD", new BigDecimal("150.00"), List.of(
                        new CaptureState("CT-1", new BigDecimal("100.00")),
                        new CaptureState("CT-9", new BigDecimal("50.00"))))));
        authClient = new RecordingRefundAuthorizationClient();
        service = new RefundService(refunds, orders, authClient);

        // 80.00 already refunded against ORD-1, so 70.00 remains refundable.
        service.refund(cmd("seed-refund", "80.00", RefundMode.OFFLINE));
        authClient.reset();
    }

    private RefundCommand cmd(String key, String amount, RefundMode mode) {
        return new RefundCommand(key, "CP-1", "ORD-1", null,
                new BigDecimal(amount), "USD", mode);
    }

    @Test
    void duplicateIdempotencyKeyYieldsDuplicateAndCreatesNoSecondRecord() {
        service.refund(cmd("idem-1", "25.00", RefundMode.OFFLINE));
        long afterFirst = refunds.count();

        RefundResult second = service.refund(cmd("idem-1", "25.00", RefundMode.OFFLINE));

        assertThat(second.outcome()).isEqualTo(RefundOutcome.DUPLICATE);
        assertThat(refunds.count()).isEqualTo(afterFirst);
    }

    @Test
    void refundExceedingRemainingRefundableIsRejected() {
        RefundResult r = service.refund(cmd("idem-2", "90.00", RefundMode.OFFLINE));

        assertThat(r.outcome()).isEqualTo(RefundOutcome.REJECTED);
    }

    @Test
    void refundWithinRemainingRefundableIsApproved() {
        RefundResult r = service.refund(cmd("idem-3", "50.00", RefundMode.OFFLINE));

        assertThat(r.outcome()).isEqualTo(RefundOutcome.APPROVED);
    }

    @Test
    void refundExactlyAtTheRemainingRefundableBoundaryIsApproved() {
        RefundResult r = service.refund(cmd("idem-4", "70.00", RefundMode.OFFLINE));

        assertThat(r.outcome()).isEqualTo(RefundOutcome.APPROVED);
    }

    @Test
    void onlineRefundInvokesTheAuthorizationStubAndOfflineDoesNot() {
        service.refund(cmd("idem-5", "10.00", RefundMode.ONLINE));
        assertThat(authClient.invocations()).isEqualTo(1);

        service.refund(cmd("idem-6", "10.00", RefundMode.OFFLINE));
        assertThat(authClient.invocations()).isEqualTo(1);
    }

    @Test
    void unknownOrderIsRejectedRatherThanAssumed() {
        RefundResult r = service.refund(new RefundCommand("idem-7", "CP-1", "ORD-UNKNOWN",
                null, new BigDecimal("5.00"), "USD", RefundMode.OFFLINE));

        assertThat(r.outcome()).isEqualTo(RefundOutcome.REJECTED);
    }

    @Test
    void resultReportsCapturedAndRefundedTotalsForTheResponseContract() {
        RefundResult r = service.refund(cmd("idem-8", "20.00", RefundMode.OFFLINE));

        assertThat(r.totalCapturedAmount()).isEqualByComparingTo("150.00");
        assertThat(r.totalRefundedAmount()).isEqualByComparingTo("100.00");
    }

    private RefundCommand captureCmd(String key, String amount, String captureId) {
        return new RefundCommand(key, "CP-1", "ORD-1", captureId,
                new BigDecimal(amount), "USD", RefundMode.OFFLINE);
    }

    @Test
    void refundTargetingACaptureMayNotExceedThatCapturesOwnAmount() {
        // CT-9 is a 50.00 capture. 60.00 sits inside the order's remaining 70.00 but outside the
        // capture's own 50.00, so the per-capture rule is the one that must refuse it.
        RefundResult r = service.refund(captureCmd("idem-cap-over", "60.00", "CT-9"));

        assertThat(r.outcome()).isEqualTo(RefundOutcome.REJECTED);
    }

    @Test
    void refundWithinTheTargetedCapturesAmountIsApproved() {
        RefundResult r = service.refund(captureCmd("idem-cap-ok", "40.00", "CT-9"));

        assertThat(r.outcome()).isEqualTo(RefundOutcome.APPROVED);
    }
}
