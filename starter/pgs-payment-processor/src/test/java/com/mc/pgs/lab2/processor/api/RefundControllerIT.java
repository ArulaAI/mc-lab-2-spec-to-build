package com.mc.pgs.lab2.processor.api;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.system.CapturedOutput;
import org.springframework.boot.test.system.OutputCaptureExtension;
import org.springframework.http.MediaType;
import org.springframework.test.annotation.DirtiesContext;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.ResultActions;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@DirtiesContext(classMode = DirtiesContext.ClassMode.AFTER_EACH_TEST_METHOD)
@ExtendWith(OutputCaptureExtension.class)
class RefundControllerIT {

    @Autowired
    private MockMvc mockMvc;

    private static String body(String orderId, String amount, boolean online, String targetTransactionId) {
        String target = targetTransactionId == null ? "null" : "\"" + targetTransactionId + "\"";
        return """
               {
                 "merchantWsApiId": "MERCH-1",
                 "wsApiSupport": {
                   "transactionWsApiId": "TXN-1",
                   "orderWsApiId": "%s",
                   "wsApiVersion": "62",
                   "targetTransactionWsApiId": %s,
                   "refundAuthorization": %s
                 },
                 "amounts": { "transactionAmount": %s },
                 "paymentCurrency": "USD",
                 "merchantOrder": { "transactionReference": "REF-1" }
               }
               """.formatted(orderId, target, online, amount);
    }

    private ResultActions postRefund(String path, String json, String idempotencyKey) throws Exception {
        return mockMvc.perform(post(path)
                .header("Idempotency-Key", idempotencyKey)
                .contentType(MediaType.APPLICATION_JSON)
                .content(json));
    }

    @Test
    void approvedRefundReturns200WithOrderTotals() throws Exception {
        postRefund("/card-payments/CP-1/refunds", body("ORD-1", "25.00", false, null), "idem-1")
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.order.totalCapturedAmount").value(150.00))
                .andExpect(jsonPath("$.order.totalRefundedAmount").value(25.00))
                .andExpect(jsonPath("$.order.status").value("PARTIALLY_REFUNDED"));
    }

    @Test
    void duplicateRefundReturns409() throws Exception {
        String json = body("ORD-1", "25.00", false, null);
        postRefund("/card-payments/CP-1/refunds", json, "idem-dup").andExpect(status().isOk());
        postRefund("/card-payments/CP-1/refunds", json, "idem-dup").andExpect(status().isConflict());
    }

    @Test
    void captureTargetedRefundIsAcceptedOnTheCaptureEndpoint() throws Exception {
        postRefund("/card-payments/CP-1/card-captures/CT-9/refunds",
                body("ORD-1", "25.00", false, "CT-9"), "idem-cap")
                .andExpect(status().isOk());
    }

    @Test
    void refundExceedingRemainingRefundableReturns400() throws Exception {
        postRefund("/card-payments/CP-1/refunds", body("ORD-SMALL", "99.00", false, null), "idem-big")
                .andExpect(status().isBadRequest());
    }

    @Test
    void negativeAmountIsRejectedAtTheBoundaryWith400() throws Exception {
        postRefund("/card-payments/CP-1/refunds", body("ORD-1", "-5.00", false, null), "idem-neg")
                .andExpect(status().isBadRequest());
    }

    @Test
    void missingIdempotencyKeyHeaderIsRejectedWith400() throws Exception {
        mockMvc.perform(post("/card-payments/CP-1/refunds")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(body("ORD-1", "25.00", false, null)))
                .andExpect(status().isBadRequest());
    }

    @Test
    void errorResponsesLeakNoInternalDetail() throws Exception {
        String response = postRefund("/card-payments/CP-1/refunds",
                body("ORD-1", "-5.00", false, null), "idem-leak")
                .andReturn().getResponse().getContentAsString();

        assertThat(response).doesNotContain("com.mc.pgs").doesNotContain("Exception");
    }

    @Test
    void authorizationCodeIsNeverWrittenToTheLog(CapturedOutput output) throws Exception {
        String response = postRefund("/card-payments/CP-1/refunds",
                body("ORD-1", "25.00", true, null), "idem-online")
                .andExpect(status().isOk())
                .andReturn().getResponse().getContentAsString();

        assertThat(response).contains("APR");           // the caller does receive it
        assertThat(output.getAll()).doesNotContain("APR"); // the log never does
    }
}
