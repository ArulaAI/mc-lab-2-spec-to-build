package com.mc.pgs.lab2.tta.client.contract;

import java.net.URI;
import java.util.Objects;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonCreator;
import com.mc.pgs.lab2.tta.client.contract.AuthorizationResponse;
import java.time.OffsetDateTime;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;


import java.util.*;
import jakarta.annotation.Generated;

/**
 * ResponseTransaction
 */

@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", comments = "Generator version: 7.8.0")
public class ResponseTransaction {

  private AuthorizationResponse authorizationResponse;

  public ResponseTransaction authorizationResponse(AuthorizationResponse authorizationResponse) {
    this.authorizationResponse = authorizationResponse;
    return this;
  }

  /**
   * Get authorizationResponse
   * @return authorizationResponse
   */
  @Valid 
  @JsonProperty("authorizationResponse")
  public AuthorizationResponse getAuthorizationResponse() {
    return authorizationResponse;
  }

  public void setAuthorizationResponse(AuthorizationResponse authorizationResponse) {
    this.authorizationResponse = authorizationResponse;
  }

  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    ResponseTransaction responseTransaction = (ResponseTransaction) o;
    return Objects.equals(this.authorizationResponse, responseTransaction.authorizationResponse);
  }

  @Override
  public int hashCode() {
    return Objects.hash(authorizationResponse);
  }

  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class ResponseTransaction {\n");
    sb.append("    authorizationResponse: ").append(toIndentedString(authorizationResponse)).append("\n");
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

