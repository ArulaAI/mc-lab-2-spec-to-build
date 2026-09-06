package com.mc.pgs.lab2.processor.repo;

import com.mc.pgs.lab2.processor.domain.RefundMode;
import com.mc.pgs.lab2.processor.domain.RefundRecord;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.math.BigDecimal;
import static org.assertj.core.api.Assertions.assertThat;

class InMemoryRefundRecordRepositoryTest {

    private InMemoryRefundRecordRepository repo;

    @BeforeEach
    void setUp() {
        repo = new InMemoryRefundRecordRepository();
    }

    private RefundRecord rec(String key, String amount) {
        return RefundRecord.approved(key, "ORD-1", null, new BigDecimal(amount),
                "USD", RefundMode.OFFLINE, "APR000");
    }

    @Test
    void savingTheSameIdempotencyKeyTwiceStoresOneRecord() {
        repo.save(rec("idem-1", "25.00"));
        repo.save(rec("idem-1", "25.00"));

        assertThat(repo.count()).isEqualTo(1);
    }

    @Test
    void lookupByIdempotencyKeyReturnsTheStoredRecord() {
        repo.save(rec("idem-1", "25.00"));

        assertThat(repo.findByIdempotencyKey("idem-1")).isPresent();
        assertThat(repo.findByIdempotencyKey("nope")).isEmpty();
    }

    @Test
    void totalRefundedForOrderSumsOnlyThatOrder() {
        repo.save(rec("idem-1", "25.00"));
        repo.save(rec("idem-2", "15.00"));
        repo.save(RefundRecord.approved("idem-3", "ORD-OTHER", null,
                new BigDecimal("99.00"), "USD", RefundMode.OFFLINE, "APR000"));

        assertThat(repo.totalRefundedForOrder("ORD-1")).isEqualByComparingTo("40.00");
    }
}
