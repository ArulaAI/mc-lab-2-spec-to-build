package com.mc.pgs.lab2.pair;

import com.mc.pgs.lab2.pair.support.*;
import org.junit.jupiter.api.*;

import java.net.http.HttpResponse;

import static org.assertj.core.api.Assertions.assertThat;

/** Failure semantics are part of the contract. */
class ErrorSemanticPreservationIT {

    private static ServiceLauncher processor;
    private static ServiceLauncher tta;

    @BeforeAll
    static void startPair() {
        processor = ServiceLauncher.startProcessor();
        tta = ServiceLauncher.startTta(processor.baseUrl());
    }

    @AfterAll
    static void stopPair() {
        if (tta != null) tta.close();
        if (processor != null) processor.close();
    }

    @Test
    void duplicateConflictReachesTheCallerAsAConflictNotAServerError() {
        String body = RefundBodies.wsapi("semantic-dup", "15.00", true, null);
        Http.postJson(tta.baseUrl() + "/refunds", body, null);

        HttpResponse<String> retry = Http.postJson(tta.baseUrl() + "/refunds", body, null);

        assertThat(retry.statusCode())
                .as("a duplicate answered downstream with 409 must not reach the caller as a 500: "
                        + "the caller would retry a request that was correctly refused")
                .isEqualTo(409);
    }

    @Test
    void businessRejectionReachesTheCallerAsAClientError() {
        // 999.00 exceeds the remaining refundable amount on ORD-1.
        HttpResponse<String> response = Http.postJson(tta.baseUrl() + "/refunds",
                RefundBodies.wsapi("semantic-excess", "999.00", false, null), null);

        assertThat(response.statusCode()).isEqualTo(400);
    }

    @Test
    void errorBodiesLeakNoInternalDetail() {
        String body = RefundBodies.wsapi("semantic-leak", "999.00", false, null);
        HttpResponse<String> response = Http.postJson(tta.baseUrl() + "/refunds", body, null);

        assertThat(response.body()).doesNotContain("com.mc.pgs").doesNotContain("Exception");
    }
}
