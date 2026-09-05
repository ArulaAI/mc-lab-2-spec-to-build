package com.mc.pgs.lab2.processor.api;

import com.mc.pgs.lab2.processor.domain.RefundMode;
import com.mc.pgs.lab2.processor.domain.RefundOutcome;
import com.mc.pgs.lab2.processor.service.RefundCommand;
import com.mc.pgs.lab2.processor.service.RefundResult;
import com.mc.pgs.lab2.processor.service.RefundService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;

/**
 * The two source-backed refund endpoints. Which one a caller uses is determined by the
 * identifiers they supply, per {@code docs/PGS_DECISIONS.md} 3.1.
 *
 * <p>HTTP concerns only. Every refund decision belongs to {@code RefundService}.
 */
@RestController
public class RefundController {

    private final RefundService refundService;

    public RefundController(RefundService refundService) {
        this.refundService = refundService;
    }

    /** Payment-target refund: the caller supplied an order and its original payment transaction. */
    @PostMapping("/card-payments/{cardPaymentGatewayId}/refunds")
    public ResponseEntity<ProcessorRefundResponse> refundPayment(
            @PathVariable String cardPaymentGatewayId,
            @RequestHeader("Idempotency-Key") String idempotencyKey,
            @Valid @RequestBody ProcessorRefundRequest request) {

        return respond(refundService.refund(toCommand(idempotencyKey, cardPaymentGatewayId, null, request)));
    }

    /** Capture-target refund: the caller supplied a specific capture transaction to refund against. */
    @PostMapping("/card-payments/{cardPaymentGatewayId}/card-captures/{cardTransactionGatewayId}/refunds")
    public ResponseEntity<ProcessorRefundResponse> refundCapture(
            @PathVariable String cardPaymentGatewayId,
            @PathVariable String cardTransactionGatewayId,
            @RequestHeader("Idempotency-Key") String idempotencyKey,
            @Valid @RequestBody ProcessorRefundRequest request) {

        return respond(refundService.refund(
                toCommand(idempotencyKey, cardPaymentGatewayId, cardTransactionGatewayId, request)));
    }

    private RefundCommand toCommand(String idempotencyKey, String cardPaymentGatewayId,
                                    String cardTransactionGatewayId, ProcessorRefundRequest request) {
        String targetTransactionId = cardTransactionGatewayId != null
                ? cardTransactionGatewayId
                : request.wsApiSupport().targetTransactionWsApiId();

        RefundMode mode = Boolean.TRUE.equals(request.wsApiSupport().refundAuthorization())
                ? RefundMode.ONLINE
                : RefundMode.OFFLINE;

        return new RefundCommand(idempotencyKey, cardPaymentGatewayId,
                request.wsApiSupport().orderWsApiId(), targetTransactionId,
                request.amounts().transactionAmount(), request.paymentCurrency(), mode);
    }

    private ResponseEntity<ProcessorRefundResponse> respond(RefundResult result) {
        HttpStatus status = switch (result.outcome()) {
            case APPROVED -> HttpStatus.OK;
            case DUPLICATE -> HttpStatus.CONFLICT;
            case REJECTED -> HttpStatus.BAD_REQUEST;
        };

        if (result.outcome() == RefundOutcome.REJECTED) {
            return ResponseEntity.status(status).build();
        }

        return ResponseEntity.status(status).body(toResponse(result));
    }

    private ProcessorRefundResponse toResponse(RefundResult result) {
        BigDecimal captured = result.totalCapturedAmount();
        BigDecimal refunded = result.totalRefundedAmount();
        String orderStatus = refunded.compareTo(captured) >= 0 ? "REFUNDED" : "PARTIALLY_REFUNDED";

        return new ProcessorRefundResponse(
                new ProcessorRefundResponse.Order(captured, refunded, orderStatus),
                new ProcessorRefundResponse.Transaction(
                        new ProcessorRefundResponse.AuthorizationResponse(
                                result.outcome().name(),
                                result.record() == null ? null : result.record().approvalCode())));
    }
}
