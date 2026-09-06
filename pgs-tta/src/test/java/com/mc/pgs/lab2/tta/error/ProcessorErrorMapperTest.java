package com.mc.pgs.lab2.tta.error;

import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

/** Maps downstream failures onto caller-facing responses. */
class ProcessorErrorMapperTest {

    private final ProcessorErrorMapper mapper = new ProcessorErrorMapper();

    @Test
    void downstreamServerErrorRemainsAServerError() {
        assertThat(mapper.map(500).status()).isEqualTo(500);
        assertThat(mapper.map(503).status()).isEqualTo(500);
    }

    @Test
    void errorCodesCarryNoInternalDetail() {
        for (int status : new int[]{400, 403, 409, 500, 503}) {
            assertThat(mapper.map(status).code())
                    .doesNotContain("com.mc.pgs")
                    .doesNotContain("Exception");
        }
    }
}
