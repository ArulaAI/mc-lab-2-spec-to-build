package com.mc.pgs.lab2.tta.client.contract;

import java.net.URI;
import java.util.Objects;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonValue;
import java.math.BigDecimal;
import java.time.OffsetDateTime;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;


import java.util.*;
import jakarta.annotation.Generated;

/**
 * ResponseOrder
 */

@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", comments = "Generator version: 7.8.0")
public class ResponseOrder {

  private BigDecimal totalCapturedAmount;

  private BigDecimal totalRefundedAmount;

  /**
   * Gets or Sets status
   */
  public enum StatusEnum {
    REFUNDED("REFUNDED"),
    
    PARTIALLY_REFUNDED("PARTIALLY_REFUNDED");

    private String value;

    StatusEnum(String value) {
      this.value = value;
    }

    @JsonValue
    public String getValue() {
      return value;
    }

    @Override
    public String toString() {
      return String.valueOf(value);
    }

    @JsonCreator
    public static StatusEnum fromValue(String value) {
      for (StatusEnum b : StatusEnum.values()) {
        if (b.value.equals(value)) {
          return b;
        }
      }
      throw new IllegalArgumentException("Unexpected value '" + value + "'");
    }
  }

  private StatusEnum status;

  public ResponseOrder totalCapturedAmount(BigDecimal totalCapturedAmount) {
    this.totalCapturedAmount = totalCapturedAmount;
    return this;
  }

  /**
   * Get totalCapturedAmount
   * @return totalCapturedAmount
   */
  @Valid 
  @JsonProperty("totalCapturedAmount")
  public BigDecimal getTotalCapturedAmount() {
    return totalCapturedAmount;
  }

  public void setTotalCapturedAmount(BigDecimal totalCapturedAmount) {
    this.totalCapturedAmount = totalCapturedAmount;
  }

  public ResponseOrder totalRefundedAmount(BigDecimal totalRefundedAmount) {
    this.totalRefundedAmount = totalRefundedAmount;
    return this;
  }

  /**
   * Get totalRefundedAmount
   * @return totalRefundedAmount
   */
  @Valid 
  @JsonProperty("totalRefundedAmount")
  public BigDecimal getTotalRefundedAmount() {
    return totalRefundedAmount;
  }

  public void setTotalRefundedAmount(BigDecimal totalRefundedAmount) {
    this.totalRefundedAmount = totalRefundedAmount;
  }

  public ResponseOrder status(StatusEnum status) {
    this.status = status;
    return this;
  }

  /**
   * Get status
   * @return status
   */
  
  @JsonProperty("status")
  public StatusEnum getStatus() {
    return status;
  }

  public void setStatus(StatusEnum status) {
    this.status = status;
  }

  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    ResponseOrder responseOrder = (ResponseOrder) o;
    return Objects.equals(this.totalCapturedAmount, responseOrder.totalCapturedAmount) &&
        Objects.equals(this.totalRefundedAmount, responseOrder.totalRefundedAmount) &&
        Objects.equals(this.status, responseOrder.status);
  }

  @Override
  public int hashCode() {
    return Objects.hash(totalCapturedAmount, totalRefundedAmount, status);
  }

  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class ResponseOrder {\n");
    sb.append("    totalCapturedAmount: ").append(toIndentedString(totalCapturedAmount)).append("\n");
    sb.append("    totalRefundedAmount: ").append(toIndentedString(totalRefundedAmount)).append("\n");
    sb.append("    status: ").append(toIndentedString(status)).append("\n");
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

