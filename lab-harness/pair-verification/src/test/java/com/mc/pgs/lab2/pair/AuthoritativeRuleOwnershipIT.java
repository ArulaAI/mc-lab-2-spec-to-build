package com.mc.pgs.lab2.pair;

import com.mc.pgs.lab2.pair.support.*;
import org.junit.jupiter.api.*;

import java.net.http.HttpResponse;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * The remaining-refundable determination depends on order state only Payment Processor holds.
 *
 * <p>ORD-1 carries two captures, C1 = 100.00 and C2 = 50.00, so 150.00 is refundable in total. A
 * consumer holding a stale view of that order — one that knows only about the first capture —
 * would refuse a refund the processor would have accepted. The refusal never reaches the
 * processor, so nothing downstream reports a problem and both services still look healthy.
 */
class AuthoritativeRuleOwnershipIT {

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
    void aRefundWithinTheAuthoritativeRemainingAmountIsAccepted() {
        // Take the order to 80.00 refunded, leaving 70.00 of the 150.00 captured.
        assertThat(Http.postJson(tta.baseUrl() + "/refunds",
                RefundBodies.wsapi("ownership-seed", "80.00", false, null), null).statusCode())
                .isEqualTo(200);

        HttpResponse<String> response = Http.postJson(tta.baseUrl() + "/refunds",
                RefundBodies.wsapi("ownership-1", "50.00", false, null), null);

        assertThat(response.statusCode())
                .as("50.00 sits inside the 70.00 that actually remains refundable; only the "
                        + "processor can make that determination, so the consumer must forward it")
                .isEqualTo(200);
    }

    @Test
    void aRefundBeyondTheAuthoritativeRemainingAmountIsRefusedByTheProcessor() {
        HttpResponse<String> response = Http.postJson(tta.baseUrl() + "/refunds",
                RefundBodies.wsapi("ownership-2", "500.00", false, null), null);

        assertThat(response.statusCode()).isEqualTo(400);
    }
}
