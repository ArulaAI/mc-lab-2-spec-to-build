package com.mc.pgs.lab2.processor.domain;

/**
 * Whether a refund is processed offline against an existing PAYMENT or CAPTURE, or online with
 * an authorization leg.
 *
 * <p>Per {@code docs/PGS_DECISIONS.md} 7.2 this state is an <em>input</em> supplied to the
 * represented seam. Neither this service nor TTA owns the wider decision, which belongs to CPC
 * and is not modelled here.
 */
public enum RefundMode {
    OFFLINE,
    ONLINE
}
