package com.mc.pgs.lab2.tta.service;

import com.mc.pgs.lab2.tta.client.PaymentProcessorClient;
import com.mc.pgs.lab2.tta.client.ProcessorCallResult;
import com.mc.pgs.lab2.tta.client.contract.*;
import com.mc.pgs.lab2.tta.error.ProcessorErrorMapper;
import com.mc.pgs.lab2.tta.mapping.RefundRequestMapper;
import com.mc.pgs.lab2.tta.mapping.RefundResponseMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

import static com.mc.pgs.lab2.tta.WsapiRefundRequestFixtures.*;
import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

class RefundTranslationServiceTest {

    private PaymentProcessorClient processor;
    private RefundTranslationService service;
    private final List<String> keysSent = new ArrayList<>();

    @BeforeEach
    void setUp() {
        processor = mock(PaymentProcessorClient.class);
        keysSent.clear();

        when(processor.submitRefund(any(), anyString(), anyString(), any()))
                .thenAnswer(inv -> {
                    keysSent.add(inv.getArgument(1));
                    return new ProcessorCallResult(200, okResponse());
                });

        service = new RefundTranslationService(
                processor, new RefundRequestMapper(), new RefundResponseMapper(),
                new ProcessorErrorMapper(), new LocalRefundLimitRule(new BigDecimal("100.00")), "CP-1");
    }

    private static ProcessorRefundResponse okResponse() {
        return new ProcessorRefundResponse()
                .order(new ResponseOrder()
                        .totalCapturedAmount(new BigDecimal("150.00"))
                        .totalRefundedAmount(new BigDecimal("25.00"))
                        .status(ResponseOrder.StatusEnum.PARTIALLY_REFUNDED))
                .transaction(new ResponseTransaction()
                        .authorizationResponse(new AuthorizationResponse()
                                .responseCode("APPROVED").approvalCode("APR1")));
    }

    @Test
    void aRefundWithinTheCapturedAmountIsSentDownstream() {
        service.translate(paymentTargetRequest("idem-1", "90.00"));

        verify(processor, times(1)).submitRefund(any(), anyString(), anyString(), any());
    }

    @Test
    void incomingIdempotencyIdentityReachesTheProcessorOnTheOfflinePath() {
        service.translate(paymentTargetRequest("idem-offline", "10.00"));

        assertThat(keysSent).containsExactly("idem-offline");
    }

    @Test
    void captureTargetedRequestIsForwardedWithItsTargetTransactionIdentifier() {
        service.translate(captureTargetRequest("idem-cap", "10.00"));

        verify(processor).submitRefund(any(), eq("idem-cap"), eq("CP-1"), eq("CT-9"));
    }

    @Test
    void aRefundBeyondTheCapturedAmountOnRecordIsRejectedBeforeItIsSent() {
        TranslationResult result = service.translate(paymentTargetRequest("idem-big", "500.00"));

        assertThat(result.status()).isEqualTo(400);
        verify(processor, never()).submitRefund(any(), anyString(), anyString(), any());
    }

    @Test
    void successfulRefundIsMappedBackToTheCallerFacingShape() {
        TranslationResult result = service.translate(paymentTargetRequest("idem-ok", "25.00"));

        assertThat(result.status()).isEqualTo(200);
        assertThat(result.body().order().totalRefundedAmount()).isEqualByComparingTo("25.00");
    }
}
