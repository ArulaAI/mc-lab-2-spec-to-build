package com.mc.pgs.lab2.pair;

import com.mc.pgs.lab2.pair.support.*;
import org.junit.jupiter.api.*;

import java.net.http.HttpResponse;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Compatibility matrix cell 2 of 4: an un-upgraded consumer against the upgraded producer.
 *
 * <p>This is the cell that proves the <em>first</em> deployment step is safe. The version 2
 * contract is additive: the capture-refund endpoint is new, and {@code refundAuthorization} is new
 * and optional, defaulting to offline when absent. A consumer that has not been upgraded keeps
 * working against it unchanged.
 */
class OldConsumerAgainstNewProducerCompatibilityIT {

    private static ServiceLauncher processor;

    @BeforeAll
    static void startProducer() {
        processor = ServiceLauncher.startProcessor();
    }

    @AfterAll
    static void stopProducer() {
        if (processor != null) processor.close();
    }

    @Test
    void aVersion1ShapedRequestIsStillAcceptedByTheCurrentProducer() {
        HttpResponse<String> response = Http.postJson(
                processor.baseUrl() + "/card-payments/CP-1/refunds",
                RefundBodies.processorV1Shaped("20.00"),
                "compat-v1-1");

        assertThat(response.statusCode())
                .as("the version 2 contract is additive, so a version 1 consumer must keep working "
                        + "against it: this is what makes producer-first a safe first step here")
                .isEqualTo(200);
    }

    @Test
    void anAbsentRefundAuthorizationFieldIsTreatedAsOffline() {
        HttpResponse<String> response = Http.postJson(
                processor.baseUrl() + "/card-payments/CP-1/refunds",
                RefundBodies.processorV1Shaped("5.00"),
                "compat-v1-2");

        assertThat(response.statusCode()).isEqualTo(200);
        assertThat(response.body())
                .as("an offline refund performs no authorization, so no approval code is returned")
                .contains("\"approvalCode\":null");
    }
}
