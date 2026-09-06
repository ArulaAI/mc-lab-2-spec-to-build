package com.mc.pgs.lab2.tta.service;

import com.mc.pgs.lab2.tta.model.WsapiRefundResponse;

/** The outcome of translating one refund across the seam. */
public record TranslationResult(int status, WsapiRefundResponse body, String errorCode) {
}
