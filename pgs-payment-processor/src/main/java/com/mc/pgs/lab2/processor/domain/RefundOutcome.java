package com.mc.pgs.lab2.processor.domain;

/** Outcome of a refund decision made by this service. */
public enum RefundOutcome {
    /** Accepted and recorded. */
    APPROVED,
    /** A refund already exists for this idempotency identity. No second record was created. */
    DUPLICATE,
    /** Refused by a business rule this service is authoritative for. */
    REJECTED
}
