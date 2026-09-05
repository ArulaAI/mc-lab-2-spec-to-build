package com.mc.pgs.lab2.tta.service;

import com.mc.pgs.lab2.tta.client.PaymentProcessorClient;
import com.mc.pgs.lab2.tta.client.ProcessorCallResult;
import com.mc.pgs.lab2.tta.error.ProcessorError;
import com.mc.pgs.lab2.tta.error.ProcessorErrorMapper;
import com.mc.pgs.lab2.tta.mapping.RefundRequestMapper;
import com.mc.pgs.lab2.tta.mapping.RefundResponseMapper;
import com.mc.pgs.lab2.tta.model.WsapiRefundRequest;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

/**
 * Translates a WSAPI-shaped refund onto the Payment Processor contract, and translates the answer
 * back.
 */
@Service
public class RefundTranslationService {

    private static final Logger log = LoggerFactory.getLogger(RefundTranslationService.class);

    private final PaymentProcessorClient processor;
    private final RefundRequestMapper requestMapper;
    private final RefundResponseMapper responseMapper;
    private final ProcessorErrorMapper errorMapper;
    private final LocalRefundLimitRule refundLimitRule;
    private final String cardPaymentGatewayId;

    public RefundTranslationService(PaymentProcessorClient processor,
                                    RefundRequestMapper requestMapper,
                                    RefundResponseMapper responseMapper,
                                    ProcessorErrorMapper errorMapper,
                                    LocalRefundLimitRule refundLimitRule,
                                    @Value("${processor.card-payment-gateway-id}") String cardPaymentGatewayId) {
        this.processor = processor;
        this.requestMapper = requestMapper;
        this.responseMapper = responseMapper;
        this.errorMapper = errorMapper;
        this.refundLimitRule = refundLimitRule;
        this.cardPaymentGatewayId = cardPaymentGatewayId;
    }

    public TranslationResult translate(WsapiRefundRequest request) {
        String idempotencyKey = requestMapper.idempotencyKeyFor(request);
        String targetTransactionId = request.isCaptureTargeted()
                ? request.transaction().targetTransactionId()
                : null;

        // Never log the request itself: it carries merchant and order identifiers and, in a real
        // deployment, would sit next to cardholder data.
        log.info("Translating refund for order {} ({} mode)",
                request.orderId(), request.isOnline() ? "online" : "offline");

        if (refundLimitRule.exceedsRemaining(request.orderId(), request.transaction().amount())) {
            log.info("Refund for order {} exceeds the captured amount on record", request.orderId());
            return new TranslationResult(400, null, "REFUND_EXCEEDS_CAPTURED_AMOUNT");
        }

        ProcessorCallResult result = processor.submitRefund(
                requestMapper.toProcessorRequest(request),
                idempotencyKey,
                cardPaymentGatewayId,
                targetTransactionId);

        if (result.isSuccess()) {
            refundLimitRule.recordRefunded(request.orderId(), request.transaction().amount());
            return new TranslationResult(result.statusCode(),
                    responseMapper.toWsapiResponse(result.body()), null);
        }

        ProcessorError error = errorMapper.map(result.statusCode());
        log.info("Refund for order {} was not processed downstream: {}", request.orderId(), error.code());
        return new TranslationResult(error.status(), null, error.code());
    }
}
