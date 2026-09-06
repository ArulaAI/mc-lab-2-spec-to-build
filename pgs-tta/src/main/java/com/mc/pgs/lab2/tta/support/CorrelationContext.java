package com.mc.pgs.lab2.tta.support;

/**
 * Correlation identity for one refund as it crosses the seam.
 *
 * <p>Grounding split, and it matters: propagating a correlation ID across every service hop is a
 * stated non-negotiable. The specific header name used here is <strong>lab representation</strong>
 * (docs/PGS_DECISIONS.md 8.2). The correlation headers named in the supplied material belong to a
 * different API, and this lab does not present its choice as the PGS refund-path header.
 */
public final class CorrelationContext {

    /** LAB REPRESENTATION - not a PGS-published refund-path header. */
    public static final String CORRELATION_ID_HEADER = "X-Correlation-Id";

    private CorrelationContext() {
    }
}
