package com.mc.pgs.lab2.processor.domain;

import org.junit.jupiter.api.Test;
import java.math.BigDecimal;
import static org.assertj.core.api.Assertions.assertThat;

class RefundRecordTest {

    @Test
    void refundRecordCarriesIdempotencyIdentityAndOutcome() {
        RefundRecord r = RefundRecord.approved("idem-1", "ORD-1", null,
                new BigDecimal("25.00"), "USD", RefundMode.OFFLINE, "APR123");

        assertThat(r.idempotencyKey()).isEqualTo("idem-1");
        assertThat(r.outcome()).isEqualTo(RefundOutcome.APPROVED);
        assertThat(r.mode()).isEqualTo(RefundMode.OFFLINE);
    }

    @Test
    void captureTargetedRefundRetainsTheTargetTransactionIdentifier() {
        RefundRecord r = RefundRecord.approved("idem-2", "ORD-1", "CT-9",
                new BigDecimal("10.00"), "USD", RefundMode.ONLINE, "APR456");

        assertThat(r.targetTransactionId()).isEqualTo("CT-9");
    }
}
