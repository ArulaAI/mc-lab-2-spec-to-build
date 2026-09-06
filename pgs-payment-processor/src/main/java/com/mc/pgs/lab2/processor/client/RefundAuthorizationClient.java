package com.mc.pgs.lab2.processor.client;

import java.math.BigDecimal;

/**
 * The authorization leg of an online refund.
 *
 * <p>Lab representation: every implementation here is deterministic and makes no network call.
 * The real authorization path is outside the represented seam.
 */
public interface RefundAuthorizationClient {

    String authorize(String orderId, BigDecimal amount, String currency);
}
