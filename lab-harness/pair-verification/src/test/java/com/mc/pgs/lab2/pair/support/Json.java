package com.mc.pgs.lab2.pair.support;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.math.BigDecimal;

/** Reads a single value out of a seam response, so assertions can be about numbers, not substrings. */
public final class Json {

    private static final ObjectMapper MAPPER = new ObjectMapper();

    private Json() {
    }

    public static BigDecimal totalRefundedAmount(String body) {
        try {
            JsonNode node = MAPPER.readTree(body).at("/order/totalRefundedAmount");
            if (node.isMissingNode() || node.isNull()) {
                throw new IllegalStateException("no /order/totalRefundedAmount in response: " + body);
            }
            return node.decimalValue();
        } catch (Exception ex) {
            throw new IllegalStateException("could not read the refunded total from: " + body, ex);
        }
    }
}
