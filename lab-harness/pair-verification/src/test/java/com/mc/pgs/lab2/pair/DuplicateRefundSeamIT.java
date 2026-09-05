package com.mc.pgs.lab2.pair;

import com.mc.pgs.lab2.pair.support.*;
import org.junit.jupiter.api.*;

import java.math.BigDecimal;
import java.net.http.HttpResponse;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * End-to-end idempotency is a property of the pair, not of either service.
 *
 * <p>Both services can contain correct-looking idempotency logic while the operation as a whole is
 * not idempotent, because the retry identity one side sends is not the identity the other side
 * deduplicates against.
 */
class DuplicateRefundSeamIT {

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
    void onlineRetryYieldsConflictAndNoSecondRefund() {
        String body = RefundBodies.wsapi("dup-online", "25.00", true, null);

        HttpResponse<String> first = Http.postJson(tta.baseUrl() + "/refunds", body, null);
        assertThat(first.statusCode()).isEqualTo(200);
        BigDecimal afterFirst = Json.totalRefundedAmount(first.body());

        HttpResponse<String> retry = Http.postJson(tta.baseUrl() + "/refunds", body, null);
        assertThat(retry.statusCode())
                .as("the same logical refund submitted twice must conflict, not refund twice")
                .isEqualTo(409);

        // Prove no second refund landed by measuring the change the next refund produces. Asserting
        // on a running total would be order-dependent, since sibling tests refund against the same
        // order and JUnit does not guarantee method order.
        HttpResponse<String> probe = Http.postJson(tta.baseUrl() + "/refunds",
                RefundBodies.wsapi("dup-online-probe", "5.00", true, null), null);
        assertThat(probe.statusCode()).isEqualTo(200);

        assertThat(Json.totalRefundedAmount(probe.body()).subtract(afterFirst))
                .as("only the 5.00 probe may have been added; a larger delta means the retry "
                        + "refunded a second time")
                .isEqualByComparingTo("5.00");
    }

    @Test
    void offlineRetryYieldsConflictToo() {
        String body = RefundBodies.wsapi("dup-offline", "12.00", false, null);

        assertThat(Http.postJson(tta.baseUrl() + "/refunds", body, null).statusCode()).isEqualTo(200);
        assertThat(Http.postJson(tta.baseUrl() + "/refunds", body, null).statusCode()).isEqualTo(409);
    }
}
