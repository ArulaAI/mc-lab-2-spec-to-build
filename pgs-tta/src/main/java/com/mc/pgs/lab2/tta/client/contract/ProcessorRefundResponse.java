package com.mc.pgs.lab2.tta.client.contract;

import java.net.URI;
import java.util.Objects;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonCreator;
import com.mc.pgs.lab2.tta.client.contract.ResponseOrder;
import com.mc.pgs.lab2.tta.client.contract.ResponseTransaction;
import java.time.OffsetDateTime;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;


import java.util.*;
import jakarta.annotation.Generated;

/**
 * ProcessorRefundResponse
 */

@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", comments = "Generator version: 7.8.0")
public class ProcessorRefundResponse {

  private ResponseOrder order;

  private ResponseTransaction transaction;

  public ProcessorRefundResponse order(ResponseOrder order) {
    this.order = order;
    return this;
  }

  /**
   * Get order
   * @return order
   */
  @Valid 
  @JsonProperty("order")
  public ResponseOrder getOrder() {
    return order;
  }

  public void setOrder(ResponseOrder order) {
    this.order = order;
  }

  public ProcessorRefundResponse transaction(ResponseTransaction transaction) {
    this.transaction = transaction;
    return this;
  }

  /**
   * Get transaction
   * @return transaction
   */
  @Valid 
  @JsonProperty("transaction")
  public ResponseTransaction getTransaction() {
    return transaction;
  }

  public void setTransaction(ResponseTransaction transaction) {
    this.transaction = transaction;
  }

  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    ProcessorRefundResponse processorRefundResponse = (ProcessorRefundResponse) o;
    return Objects.equals(this.order, processorRefundResponse.order) &&
        Objects.equals(this.transaction, processorRefundResponse.transaction);
  }

  @Override
  public int hashCode() {
    return Objects.hash(order, transaction);
  }

  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class ProcessorRefundResponse {\n");
    sb.append("    order: ").append(toIndentedString(order)).append("\n");
    sb.append("    transaction: ").append(toIndentedString(transaction)).append("\n");
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

