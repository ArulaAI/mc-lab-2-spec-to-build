package com.mc.pgs.lab2.pair;

import com.mc.pgs.lab2.pair.support.*;
import org.junit.jupiter.api.*;

import java.net.http.HttpResponse;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Compatibility matrix cell 3 of 4: the upgraded consumer against an un-upgraded producer.
 *
 * <p>This test <strong>passes by detecting the incompatibility</strong>. It is diagnostic, not
 * permanently red: it asserts that the reverse rollout order is rejected, which is the evidence
 * that deploying the consumer first would break production.
 *
 * <p>The rule this supports is not "always deploy the producer first". It is: derive a sequence in
 * which old and new can coexist safely. For <em>this</em> additive change that sequence happens to
 * be producer first, and the evidence is here rather than in an assertion from a facilitator.
 */
class ReverseOrderDiagnosticIT {

    private static OldProcessorV1Stub oldProcessor;
    private static ServiceLauncher newTta;

    @BeforeAll
    static void startReversePair() throws Exception {
        oldProcessor = OldProcessorV1Stub.start();
        newTta = ServiceLauncher.startTta(oldProcessor.baseUrl());
    }

    @AfterAll
    static void stopReversePair() {
        if (newTta != null) newTta.close();
        if (oldProcessor != null) oldProcessor.close();
    }

    @Test
    void newConsumerAgainstOldProducerIsRejected_provingReverseRolloutUnsafe() {
        HttpResponse<String> response = Http.postJson(newTta.baseUrl() + "/refunds",
                RefundBodies.wsapi("reverse-1", "25.00", true, "CT-9"), null);

        assertThat(response.statusCode())
                .as("the upgraded consumer targets the capture-refund endpoint, which contract "
                        + "version 1 never published; deploying the consumer first would fail in "
                        + "production exactly like this")
                .isEqualTo(404);
    }

    @Test
    void thePaymentTargetedPathStillWorksAgainstTheOldProducer() {
        // Not everything breaks, which is what makes the reverse order deceptively survivable in
        // a smoke test that only exercises the payment-targeted path.
        HttpResponse<String> response = Http.postJson(newTta.baseUrl() + "/refunds",
                RefundBodies.wsapi("reverse-2", "25.00", false, null), null);

        assertThat(response.statusCode()).isEqualTo(200);
    }
}
