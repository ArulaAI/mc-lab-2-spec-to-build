package com.mc.pgs.lab2.tta.error;

import org.springframework.stereotype.Component;

/**
 * Maps a downstream failure onto the response this service returns to its caller.
 */
@Component
public class ProcessorErrorMapper {

    public ProcessorError map(int downstreamStatus) {
        // A refund that the processor did not accept is reported to the caller as a processing
        // failure. No downstream detail is exposed.
        return new ProcessorError(500, "SYSTEM_ERROR");
    }
}
