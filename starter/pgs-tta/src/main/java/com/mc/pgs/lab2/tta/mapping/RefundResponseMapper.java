package com.mc.pgs.lab2.tta.mapping;

import com.mc.pgs.lab2.tta.client.contract.ProcessorRefundResponse;
import com.mc.pgs.lab2.tta.model.WsapiRefundResponse;
import org.springframework.stereotype.Component;

@Component
public class RefundResponseMapper {

    public WsapiRefundResponse toWsapiResponse(ProcessorRefundResponse src) {
        if (src == null) {
            return null;
        }
        WsapiRefundResponse.Order order = src.getOrder() == null ? null
                : new WsapiRefundResponse.Order(
                        src.getOrder().getTotalCapturedAmount(),
                        src.getOrder().getTotalRefundedAmount(),
                        src.getOrder().getStatus() == null ? null : src.getOrder().getStatus().getValue());

        WsapiRefundResponse.Transaction transaction =
                src.getTransaction() == null || src.getTransaction().getAuthorizationResponse() == null
                        ? null
                        : new WsapiRefundResponse.Transaction(
                                src.getTransaction().getAuthorizationResponse().getResponseCode(),
                                src.getTransaction().getAuthorizationResponse().getApprovalCode());

        return new WsapiRefundResponse(order, transaction);
    }
}
