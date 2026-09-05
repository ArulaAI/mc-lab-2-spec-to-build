package com.mc.pgs.lab2.tta.client.contract;

import java.net.URI;
import java.util.Objects;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonCreator;
import java.time.OffsetDateTime;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;


import java.util.*;
import jakarta.annotation.Generated;

/**
 * WsApiSupport
 */

@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", comments = "Generator version: 7.8.0")
public class WsApiSupport {

  private String transactionWsApiId;

  private String orderWsApiId;

  private String wsApiVersion;

  private String targetTransactionWsApiId;

  public WsApiSupport() {
    super();
  }

  /**
   * Constructor with only required parameters
   */
  public WsApiSupport(String transactionWsApiId, String orderWsApiId) {
    this.transactionWsApiId = transactionWsApiId;
    this.orderWsApiId = orderWsApiId;
  }

  public WsApiSupport transactionWsApiId(String transactionWsApiId) {
    this.transactionWsApiId = transactionWsApiId;
    return this;
  }

  /**
   * Get transactionWsApiId
   * @return transactionWsApiId
   */
  @NotNull 
  @JsonProperty("transactionWsApiId")
  public String getTransactionWsApiId() {
    return transactionWsApiId;
  }

  public void setTransactionWsApiId(String transactionWsApiId) {
    this.transactionWsApiId = transactionWsApiId;
  }

  public WsApiSupport orderWsApiId(String orderWsApiId) {
    this.orderWsApiId = orderWsApiId;
    return this;
  }

  /**
   * Get orderWsApiId
   * @return orderWsApiId
   */
  @NotNull 
  @JsonProperty("orderWsApiId")
  public String getOrderWsApiId() {
    return orderWsApiId;
  }

  public void setOrderWsApiId(String orderWsApiId) {
    this.orderWsApiId = orderWsApiId;
  }

  public WsApiSupport wsApiVersion(String wsApiVersion) {
    this.wsApiVersion = wsApiVersion;
    return this;
  }

  /**
   * Get wsApiVersion
   * @return wsApiVersion
   */
  
  @JsonProperty("wsApiVersion")
  public String getWsApiVersion() {
    return wsApiVersion;
  }

  public void setWsApiVersion(String wsApiVersion) {
    this.wsApiVersion = wsApiVersion;
  }

  public WsApiSupport targetTransactionWsApiId(String targetTransactionWsApiId) {
    this.targetTransactionWsApiId = targetTransactionWsApiId;
    return this;
  }

  /**
   * Present for the capture-target case.
   * @return targetTransactionWsApiId
   */
  
  @JsonProperty("targetTransactionWsApiId")
  public String getTargetTransactionWsApiId() {
    return targetTransactionWsApiId;
  }

  public void setTargetTransactionWsApiId(String targetTransactionWsApiId) {
    this.targetTransactionWsApiId = targetTransactionWsApiId;
  }

  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    WsApiSupport wsApiSupport = (WsApiSupport) o;
    return Objects.equals(this.transactionWsApiId, wsApiSupport.transactionWsApiId) &&
        Objects.equals(this.orderWsApiId, wsApiSupport.orderWsApiId) &&
        Objects.equals(this.wsApiVersion, wsApiSupport.wsApiVersion) &&
        Objects.equals(this.targetTransactionWsApiId, wsApiSupport.targetTransactionWsApiId);
  }

  @Override
  public int hashCode() {
    return Objects.hash(transactionWsApiId, orderWsApiId, wsApiVersion, targetTransactionWsApiId);
  }

  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class WsApiSupport {\n");
    sb.append("    transactionWsApiId: ").append(toIndentedString(transactionWsApiId)).append("\n");
    sb.append("    orderWsApiId: ").append(toIndentedString(orderWsApiId)).append("\n");
    sb.append("    wsApiVersion: ").append(toIndentedString(wsApiVersion)).append("\n");
    sb.append("    targetTransactionWsApiId: ").append(toIndentedString(targetTransactionWsApiId)).append("\n");
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

