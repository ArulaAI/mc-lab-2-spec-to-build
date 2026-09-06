package com.mc.pgs.lab2.tta.mapping;

import com.mc.pgs.lab2.tta.client.contract.*;
import com.mc.pgs.lab2.tta.model.WsapiRefundRequest;
import org.springframework.stereotype.Component;

import java.util.UUID;

/**
 * Maps the WSAPI refund request onto the Payment Processor contract.
 */
@Component
public class RefundRequestMapper {

    public ProcessorRefundRequest toProcessorRequest(WsapiRefundRequest src) {
        WsApiSupport support = new WsApiSupport()
                .transactionWsApiId(src.transactionId())
                .orderWsApiId(src.orderId())
                .wsApiVersion(src.version())
                .targetTransactionWsApiId(src.isCaptureTargeted()
                        ? src.transaction().targetTransactionId() : null);

        return new ProcessorRefundRequest()
                .merchantWsApiId(src.merchantId())
                .wsApiSupport(support)
                .amounts(new Amounts().transactionAmount(src.transaction().amount()))
                .paymentCurrency(src.transaction().currency())
                .merchantOrder(new MerchantOrder().transactionReference(src.transaction().reference()));
    }

    /**
     * The reference to send downstream for this submission.
     */
    public String idempotencyKeyFor(WsapiRefundRequest src) {
        if (src.isOnline()) {
            // Online refunds go through the authorization path, so each submission is given its
            // own submission reference.
            return "tta-" + UUID.randomUUID();
        }
        return src.idempotencyKey();
    }
}
