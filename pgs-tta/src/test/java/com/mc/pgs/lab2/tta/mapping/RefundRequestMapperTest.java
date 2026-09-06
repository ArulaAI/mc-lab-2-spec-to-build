package com.mc.pgs.lab2.tta.mapping;

import com.mc.pgs.lab2.tta.client.contract.ProcessorRefundRequest;
import com.mc.pgs.lab2.tta.model.WsapiRefundRequest;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;

import static com.mc.pgs.lab2.tta.WsapiRefundRequestFixtures.*;
import static org.assertj.core.api.Assertions.assertThat;

/**
 * The mapping table in docs/PGS_DECISIONS.md section 2, asserted field by field.
 */
class RefundRequestMapperTest {

    private final RefundRequestMapper mapper = new RefundRequestMapper();

    @Test
    void everyMappedFieldLandsWhereTheSourceTableSaysItShould() {
        WsapiRefundRequest src = paymentTargetRequest("idem-1", "25.00");

        ProcessorRefundRequest out = mapper.toProcessorRequest(src);

        assertThat(out.getMerchantWsApiId()).isEqualTo("MERCH-1");
        assertThat(out.getWsApiSupport().getTransactionWsApiId()).isEqualTo("TXN-1");
        assertThat(out.getWsApiSupport().getOrderWsApiId()).isEqualTo("ORD-1");
        assertThat(out.getWsApiSupport().getWsApiVersion()).isEqualTo("62");
        assertThat(out.getAmounts().getTransactionAmount()).isEqualByComparingTo("25.00");
        assertThat(out.getPaymentCurrency()).isEqualTo("USD");
        assertThat(out.getMerchantOrder().getTransactionReference()).isEqualTo("REF-1");
    }

    @Test
    void captureTargetIdentifierIsCarriedOnlyWhenTheCallerSuppliedOne() {
        assertThat(mapper.toProcessorRequest(captureTargetRequest("idem-2", "10.00"))
                .getWsApiSupport().getTargetTransactionWsApiId()).isEqualTo("CT-9");

        assertThat(mapper.toProcessorRequest(paymentTargetRequest("idem-3", "10.00"))
                .getWsApiSupport().getTargetTransactionWsApiId()).isNull();
    }

    @Test
    void incomingIdempotencyKeyIsPropagated() {
        assertThat(mapper.idempotencyKeyFor(paymentTargetRequest("idem-6", "10.00"))).isEqualTo("idem-6");
    }

    @Test
    void monetaryAmountsSurviveMappingWithoutBinaryFloatingPointDrift() {
        ProcessorRefundRequest out = mapper.toProcessorRequest(paymentTargetRequest("idem-7", "0.10"));

        assertThat(out.getAmounts().getTransactionAmount()).isEqualByComparingTo(new BigDecimal("0.10"));
    }
}
