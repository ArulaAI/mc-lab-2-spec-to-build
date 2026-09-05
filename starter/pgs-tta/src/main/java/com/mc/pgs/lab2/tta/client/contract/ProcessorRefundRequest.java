package com.mc.pgs.lab2.tta.client.contract;

import java.net.URI;
import java.util.Objects;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonCreator;
import com.mc.pgs.lab2.tta.client.contract.Amounts;
import com.mc.pgs.lab2.tta.client.contract.MerchantOrder;
import com.mc.pgs.lab2.tta.client.contract.WsApiSupport;
import java.time.OffsetDateTime;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;


import java.util.*;
import jakarta.annotation.Generated;

/**
 * ProcessorRefundRequest
 */

@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", comments = "Generator version: 7.8.0")
public class ProcessorRefundRequest {

  private String merchantWsApiId;

  private WsApiSupport wsApiSupport;

  private Amounts amounts;

  private String paymentCurrency;

  private MerchantOrder merchantOrder;

  public ProcessorRefundRequest() {
    super();
  }

  /**
   * Constructor with only required parameters
   */
  public ProcessorRefundRequest(String merchantWsApiId, WsApiSupport wsApiSupport, Amounts amounts, String paymentCurrency) {
    this.merchantWsApiId = merchantWsApiId;
    this.wsApiSupport = wsApiSupport;
    this.amounts = amounts;
    this.paymentCurrency = paymentCurrency;
  }

  public ProcessorRefundRequest merchantWsApiId(String merchantWsApiId) {
    this.merchantWsApiId = merchantWsApiId;
    return this;
  }

  /**
   * Get merchantWsApiId
   * @return merchantWsApiId
   */
  @NotNull 
  @JsonProperty("merchantWsApiId")
  public String getMerchantWsApiId() {
    return merchantWsApiId;
  }

  public void setMerchantWsApiId(String merchantWsApiId) {
    this.merchantWsApiId = merchantWsApiId;
  }

  public ProcessorRefundRequest wsApiSupport(WsApiSupport wsApiSupport) {
    this.wsApiSupport = wsApiSupport;
    return this;
  }

  /**
   * Get wsApiSupport
   * @return wsApiSupport
   */
  @NotNull @Valid 
  @JsonProperty("wsApiSupport")
  public WsApiSupport getWsApiSupport() {
    return wsApiSupport;
  }

  public void setWsApiSupport(WsApiSupport wsApiSupport) {
    this.wsApiSupport = wsApiSupport;
  }

  public ProcessorRefundRequest amounts(Amounts amounts) {
    this.amounts = amounts;
    return this;
  }

  /**
   * Get amounts
   * @return amounts
   */
  @NotNull @Valid 
  @JsonProperty("amounts")
  public Amounts getAmounts() {
    return amounts;
  }

  public void setAmounts(Amounts amounts) {
    this.amounts = amounts;
  }

  public ProcessorRefundRequest paymentCurrency(String paymentCurrency) {
    this.paymentCurrency = paymentCurrency;
    return this;
  }

  /**
   * Get paymentCurrency
   * @return paymentCurrency
   */
  @NotNull 
  @JsonProperty("paymentCurrency")
  public String getPaymentCurrency() {
    return paymentCurrency;
  }

  public void setPaymentCurrency(String paymentCurrency) {
    this.paymentCurrency = paymentCurrency;
  }

  public ProcessorRefundRequest merchantOrder(MerchantOrder merchantOrder) {
    this.merchantOrder = merchantOrder;
    return this;
  }

  /**
   * Get merchantOrder
   * @return merchantOrder
   */
  @Valid 
  @JsonProperty("merchantOrder")
  public MerchantOrder getMerchantOrder() {
    return merchantOrder;
  }

  public void setMerchantOrder(MerchantOrder merchantOrder) {
    this.merchantOrder = merchantOrder;
  }

  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    ProcessorRefundRequest processorRefundRequest = (ProcessorRefundRequest) o;
    return Objects.equals(this.merchantWsApiId, processorRefundRequest.merchantWsApiId) &&
        Objects.equals(this.wsApiSupport, processorRefundRequest.wsApiSupport) &&
        Objects.equals(this.amounts, processorRefundRequest.amounts) &&
        Objects.equals(this.paymentCurrency, processorRefundRequest.paymentCurrency) &&
        Objects.equals(this.merchantOrder, processorRefundRequest.merchantOrder);
  }

  @Override
  public int hashCode() {
    return Objects.hash(merchantWsApiId, wsApiSupport, amounts, paymentCurrency, merchantOrder);
  }

  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class ProcessorRefundRequest {\n");
    sb.append("    merchantWsApiId: ").append(toIndentedString(merchantWsApiId)).append("\n");
    sb.append("    wsApiSupport: ").append(toIndentedString(wsApiSupport)).append("\n");
    sb.append("    amounts: ").append(toIndentedString(amounts)).append("\n");
    sb.append("    paymentCurrency: ").append(toIndentedString(paymentCurrency)).append("\n");
    sb.append("    merchantOrder: ").append(toIndentedString(merchantOrder)).append("\n");
    sb.append("}");
    return sb.toString();
  }

  /**
   * Convert the given object to string with each line indented by 4 spaces
   * (except the first line).
   */
  private String toIndentedString(Object o) {
    if (o == null) {
      return "null";
    }
    return o.toString().replace("\n", "\n    ");
  }
}

