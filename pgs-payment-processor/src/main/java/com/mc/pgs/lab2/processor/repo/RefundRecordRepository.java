package com.mc.pgs.lab2.processor.repo;

import com.mc.pgs.lab2.processor.domain.RefundRecord;
import java.math.BigDecimal;
import java.util.Optional;

public interface RefundRecordRepository {

    Optional<RefundRecord> findByIdempotencyKey(String idempotencyKey);

    RefundRecord save(RefundRecord record);

    long count();

    BigDecimal totalRefundedForOrder(String orderId);

    BigDecimal totalRefundedForCapture(String orderId, String captureTransactionId);
}
