package com.mc.pgs.lab2.processor.repo;

import com.mc.pgs.lab2.processor.domain.RefundRecord;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Lab representation of the refund store. Production persistence is Oracle; an in-memory map
 * keeps the lab offline and deterministic. See {@code docs/PGS_DECISIONS.md} 11.3.
 *
 * <p>Keyed by idempotency identity so a repeated save cannot create a second record.
 */
@Repository
public class InMemoryRefundRecordRepository implements RefundRecordRepository {

    private final Map<String, RefundRecord> byIdempotencyKey = new ConcurrentHashMap<>();

    @Override
    public Optional<RefundRecord> findByIdempotencyKey(String idempotencyKey) {
        return Optional.ofNullable(byIdempotencyKey.get(idempotencyKey));
    }

    @Override
    public RefundRecord save(RefundRecord record) {
        byIdempotencyKey.putIfAbsent(record.idempotencyKey(), record);
        return byIdempotencyKey.get(record.idempotencyKey());
    }

    @Override
    public long count() {
        return byIdempotencyKey.size();
    }

    @Override
    public BigDecimal totalRefundedForOrder(String orderId) {
        return byIdempotencyKey.values().stream()
                .filter(r -> r.orderId().equals(orderId))
                .map(RefundRecord::amount)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
    }

    @Override
    public BigDecimal totalRefundedForCapture(String orderId, String captureTransactionId) {
        return byIdempotencyKey.values().stream()
                .filter(r -> r.orderId().equals(orderId))
                .filter(r -> captureTransactionId.equals(r.targetTransactionId()))
                .map(RefundRecord::amount)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
    }
}
