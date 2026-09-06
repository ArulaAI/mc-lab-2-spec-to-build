package com.mc.pgs.lab2.tta.client;

import com.mc.pgs.lab2.tta.client.contract.ProcessorRefundResponse;

/**
 * A downstream call's outcome, status included.
 *
 * <p>The status is carried rather than thrown, because the status <em>is</em> part of the
 * contract: a duplicate answered with 409 is information the caller needs, not a failure to
 * flatten.
 */
public record ProcessorCallResult(int statusCode, ProcessorRefundResponse body) {

    public boolean isSuccess() {
        return statusCode >= 200 && statusCode < 300;
    }
}
