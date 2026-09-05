package com.mc.pgs.lab2.pair;

import org.junit.jupiter.api.Test;

import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Compares the contract the producer publishes against the contract the consumer is pinned to.
 *
 * <p>Both documents are on the classpath, so this is a mechanical check rather than a judgement:
 * either the two versions agree or they do not.
 */
class ContractVersionAlignmentIT {

    private static final Pattern INFO_VERSION =
            Pattern.compile("^\\s{2}version:\\s*\"?([^\"\\s]+)\"?\\s*$", Pattern.MULTILINE);

    private static String versionOf(String classpathResource) {
        try (InputStream in = ContractVersionAlignmentIT.class.getClassLoader()
                .getResourceAsStream(classpathResource)) {
            assertThat(in).as("contract document %s must be on the classpath", classpathResource).isNotNull();
            String text = new String(in.readAllBytes(), StandardCharsets.UTF_8);
            Matcher m = INFO_VERSION.matcher(text);
            assertThat(m.find()).as("contract %s declares an info.version", classpathResource).isTrue();
            return m.group(1);
        } catch (Exception ex) {
            throw new IllegalStateException("could not read " + classpathResource, ex);
        }
    }

    @Test
    void theConsumerIsPinnedToTheContractVersionTheProducerPublishes() {
        String producerVersion = versionOf("openapi/payment-processor-v2.yaml");
        String consumerVersion = versionOf("openapi/payment-processor.yaml");

        assertThat(consumerVersion)
                .as("the consumer's generated client is derived from the contract it pins; if that "
                        + "pin trails the producer's published contract, the two services are "
                        + "reasoning about different APIs while both look healthy alone")
                .isEqualTo(producerVersion);
    }
}
