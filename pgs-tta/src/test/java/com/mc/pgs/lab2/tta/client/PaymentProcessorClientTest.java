package com.mc.pgs.lab2.tta.client;

import com.mc.pgs.lab2.tta.config.ProcessorClientProperties;
import com.mc.pgs.lab2.tta.mapping.RefundRequestMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.MediaType;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.web.client.RestClient;

import static com.mc.pgs.lab2.tta.WsapiRefundRequestFixtures.*;
import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.*;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withStatus;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withSuccess;

/**
 */
class PaymentProcessorClientTest {

    private static final String OK_BODY = """
            {"order":{"totalCapturedAmount":150.00,"totalRefundedAmount":25.00,"status":"PARTIALLY_REFUNDED"},
             "transaction":{"authorizationResponse":{"responseCode":"APPROVED","approvalCode":"APR1"}}}
            """;

    private MockRestServiceServer server;
    private PaymentProcessorClient client;
    private final RefundRequestMapper mapper = new RefundRequestMapper();

    @BeforeEach
    void setUp() {
        RestClient.Builder builder = RestClient.builder();
        server = MockRestServiceServer.bindTo(builder).build();
        client = new PaymentProcessorClient(builder, new ProcessorClientProperties("http://processor.test"));
    }

    @Test
    void paymentTargetRequestUsesThePaymentRefundEndpoint() {
        server.expect(requestTo("http://processor.test/card-payments/CP-1/refunds"))
                .andRespond(withSuccess(OK_BODY, MediaType.APPLICATION_JSON));

        client.submitRefund(mapper.toProcessorRequest(paymentTargetRequest("idem-2", "10.00")),
                "idem-2", "CP-1", null);

        server.verify();
    }

    @Test
    void idempotencyKeyIsSentAsAHeaderOnEveryCall() {
        server.expect(requestTo("http://processor.test/card-payments/CP-1/refunds"))
                .andExpect(header("Idempotency-Key", "idem-4"))
                .andRespond(withSuccess(OK_BODY, MediaType.APPLICATION_JSON));

        client.submitRefund(mapper.toProcessorRequest(paymentTargetRequest("idem-4", "10.00")),
                "idem-4", "CP-1", null);

        server.verify();
    }

    @Test
    void downstreamConflictIsReturnedAsAStatusRatherThanThrown() {
        server.expect(requestTo("http://processor.test/card-payments/CP-1/refunds"))
                .andRespond(withStatus(org.springframework.http.HttpStatus.CONFLICT));

        ProcessorCallResult result = client.submitRefund(
                mapper.toProcessorRequest(paymentTargetRequest("idem-5", "10.00")), "idem-5", "CP-1", null);

        assertThat(result.statusCode()).isEqualTo(409);
    }
}
