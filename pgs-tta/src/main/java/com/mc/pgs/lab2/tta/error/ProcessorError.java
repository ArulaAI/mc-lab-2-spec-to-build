package com.mc.pgs.lab2.tta.error;

/** A downstream failure reduced to what the caller may see: a status and an opaque code. */
public record ProcessorError(int status, String code) {
}
