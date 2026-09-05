package com.mc.pgs.lab2.tta.api;

import com.mc.pgs.lab2.tta.model.WsapiRefundRequest;
import com.mc.pgs.lab2.tta.service.RefundTranslationService;
import com.mc.pgs.lab2.tta.service.TranslationResult;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/** HTTP concerns only. */
@RestController
public class RefundTranslationController {

    private final RefundTranslationService translationService;

    public RefundTranslationController(RefundTranslationService translationService) {
        this.translationService = translationService;
    }

    @PostMapping("/refunds")
    public ResponseEntity<?> refund(@Valid @RequestBody WsapiRefundRequest request) {
        TranslationResult result = translationService.translate(request);

        if (result.body() != null) {
            return ResponseEntity.status(result.status()).body(result.body());
        }
        return ResponseEntity.status(result.status()).body(Map.of("error", result.errorCode()));
    }
}
