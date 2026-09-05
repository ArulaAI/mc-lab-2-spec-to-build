package com.mc.pgs.lab2.pair;

import com.mc.pgs.lab2.pair.support.*;
import org.junit.jupiter.api.*;

import java.net.http.HttpResponse;

import static org.assertj.core.api.Assertions.assertThat;

/** The intended final state: current TTA against current Payment Processor. */
class CurrentPairOnlineRefundIT {

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
    void onlineCaptureTargetedRefundCrossesTheSeamSuccessfully() {
        HttpResponse<String> response = Http.postJson(tta.baseUrl() + "/refunds",
                RefundBodies.wsapi("pair-online-1", "25.00", true, "CT-9"), null);

        assertThat(response.statusCode())
                .as("a capture-targeted online refund must reach the capture-refund endpoint the "
                        + "source mapping specifies, and be processed")
                .isEqualTo(200);
        assertThat(response.body()).contains("totalRefundedAmount");
    }

    @Test
    void offlinePaymentTargetedRefundCrossesTheSeamSuccessfully() {
        HttpResponse<String> response = Http.postJson(tta.baseUrl() + "/refunds",
                RefundBodies.wsapi("pair-offline-1", "10.00", false, null), null);

        assertThat(response.statusCode()).isEqualTo(200);
    }
}
