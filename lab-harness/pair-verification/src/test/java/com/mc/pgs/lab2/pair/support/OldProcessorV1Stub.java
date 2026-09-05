package com.mc.pgs.lab2.pair.support;

import com.sun.net.httpserver.HttpServer;

import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;

/**
 * A Payment Processor still running contract version 1.
 *
 * <p>Version 1 published exactly one refund endpoint. The capture-refund endpoint did not exist
 * yet, so a request to it answers 404 — which is precisely what makes deploying a new consumer
 * ahead of the producer unsafe.
 */
public final class OldProcessorV1Stub implements AutoCloseable {

    private static final String V1_RESPONSE = """
            {"order":{"totalCapturedAmount":150.00,"totalRefundedAmount":25.00,"status":"PARTIALLY_REFUNDED"},
             "transaction":{"authorizationResponse":{"responseCode":"APPROVED","approvalCode":"APR-V1"}}}
            """;

    private final HttpServer server;

    private OldProcessorV1Stub(HttpServer server) {
        this.server = server;
    }

    public static OldProcessorV1Stub start() throws IOException {
        HttpServer server = HttpServer.create(new InetSocketAddress("localhost", 0), 0);

        server.createContext("/card-payments", exchange -> {
            String path = exchange.getRequestURI().getPath();

            // Contract version 1 has no capture-refund endpoint.
            if (path.contains("/card-captures/")) {
                respond(exchange, 404, "");
                return;
            }
            if (path.endsWith("/refunds")) {
                respond(exchange, 200, V1_RESPONSE);
                return;
            }
            respond(exchange, 404, "");
        });

        server.start();
        return new OldProcessorV1Stub(server);
    }

    private static void respond(com.sun.net.httpserver.HttpExchange exchange, int status, String body)
            throws IOException {
        byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().add("Content-Type", "application/json");
        exchange.sendResponseHeaders(status, bytes.length == 0 ? -1 : bytes.length);
        if (bytes.length > 0) {
            try (OutputStream out = exchange.getResponseBody()) {
                out.write(bytes);
            }
        }
    }

    public String baseUrl() {
        return "http://localhost:" + server.getAddress().getPort();
    }

    @Override
    public void close() {
        server.stop(0);
    }
}
