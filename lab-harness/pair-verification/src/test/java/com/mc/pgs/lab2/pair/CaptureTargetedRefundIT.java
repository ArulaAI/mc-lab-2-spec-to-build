package com.mc.pgs.lab2.pair;

import com.mc.pgs.lab2.pair.support.*;
import org.junit.jupiter.api.*;

import java.net.http.HttpResponse;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Proves the consumer reaches the endpoint the source mapping specifies.
 *
 * <p>The two refund endpoints are not interchangeable routes to the same behaviour. A refund
 * targeting a capture is bounded by that capture's own amount; a refund against the order is
 * bounded by the order total. ORD-1 carries CT-1 for 100.00 and CT-9 for 50.00.
 *
 * <p>So a 60.00 refund targeting CT-9 sits <em>inside</em> the order's remaining balance but
 * <em>outside</em> the targeted capture. If it is accepted, the request did not reach the
 * capture-refund endpoint — which is exactly the failure a "both endpoints return 200" smoke test
 * cannot see.
 */
class CaptureTargetedRefundIT {

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
    void refundBeyondTheTargetedCapturesAmountIsRefused() {
        HttpResponse<String> response = Http.postJson(tta.baseUrl() + "/refunds",
                RefundBodies.wsapi("capture-over", "60.00", false, "CT-9"), null);

        assertThat(response.statusCode())
                .as("60.00 exceeds CT-9's 50.00. Accepting it means the request was sent to the "
                        + "payment-refund endpoint instead of the capture-refund endpoint the "
                        + "source mapping specifies for a capture-targeted refund")
                .isEqualTo(400);
    }

    @Test
    void refundWithinTheTargetedCapturesAmountIsAccepted() {
        HttpResponse<String> response = Http.postJson(tta.baseUrl() + "/refunds",
                RefundBodies.wsapi("capture-within", "40.00", false, "CT-9"), null);

        assertThat(response.statusCode()).isEqualTo(200);
    }
}
