package com.mc.pgs.lab2.tta.client;

import com.mc.pgs.lab2.tta.client.contract.ProcessorRefundRequest;
import com.mc.pgs.lab2.tta.client.contract.ProcessorRefundResponse;
import com.mc.pgs.lab2.tta.config.ProcessorClientProperties;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

/**
 * Calls the Payment Processor refund API.
 *
 */
@Component
public class PaymentProcessorClient {

    static final String IDEMPOTENCY_KEY_HEADER = "Idempotency-Key";

    private final RestClient restClient;

    public PaymentProcessorClient(RestClient.Builder builder, ProcessorClientProperties properties) {
        this.restClient = builder.baseUrl(properties.baseUrl()).build();
    }

    public ProcessorCallResult submitRefund(ProcessorRefundRequest body,
                                            String idempotencyKey,
                                            String cardPaymentGatewayId,
                                            String targetTransactionId) {

        String path = selectEndpoint(cardPaymentGatewayId, targetTransactionId);

        ResponseEntity<ProcessorRefundResponse> response = restClient.post()
                .uri(path)
                .header(IDEMPOTENCY_KEY_HEADER, idempotencyKey)
                .contentType(MediaType.APPLICATION_JSON)
                .body(body)
                .retrieve()
                // Never throw on a non-2xx: the downstream status is the contract, and losing it
                // here is exactly how a duplicate-conflict becomes a generic server error.
                .onStatus(status -> true, (request, res) -> { })
                .toEntity(ProcessorRefundResponse.class);

        return new ProcessorCallResult(response.getStatusCode().value(), response.getBody());
    }

    private String selectEndpoint(String cardPaymentGatewayId, String targetTransactionId) {
        // The refund endpoint carries the target transaction in the request body.
        return "/card-payments/" + cardPaymentGatewayId + "/refunds";
    }
}
