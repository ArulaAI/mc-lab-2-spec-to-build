package com.mc.pgs.lab2.processor.client;

import java.math.BigDecimal;
import java.util.concurrent.atomic.AtomicInteger;

/** Test double that counts authorization calls, so "online authorizes, offline does not" is provable. */
public class RecordingRefundAuthorizationClient implements RefundAuthorizationClient {

    private final AtomicInteger invocations = new AtomicInteger();

    @Override
    public String authorize(String orderId, BigDecimal amount, String currency) {
        invocations.incrementAndGet();
        return "APR-TEST";
    }

    public int invocations() {
        return invocations.get();
    }

    public void reset() {
        invocations.set(0);
    }
}
