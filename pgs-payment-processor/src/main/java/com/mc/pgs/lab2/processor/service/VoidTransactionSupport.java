package com.mc.pgs.lab2.processor.service;

import com.mc.pgs.lab2.processor.domain.RefundRecord;
import com.mc.pgs.lab2.processor.repo.RefundRecordRepository;

import java.util.Optional;

/**
 * Helpers for reversing a transaction before it settles.
 *
 * <p>Carried over from the earlier transaction-processing work. Shares the refund record store, so
 * the lookup helpers here are the same ones the refund path uses.
 */
public class VoidTransactionSupport {

    private final RefundRecordRepository refunds;

    public VoidTransactionSupport(RefundRecordRepository refunds) {
        this.refunds = refunds;
    }

    public Optional<RefundRecord> findReversible(String idempotencyKey) {
        return refunds.findByIdempotencyKey(idempotencyKey);
    }

    public boolean isReversible(String idempotencyKey) {
        return findReversible(idempotencyKey).isPresent();
    }
}
