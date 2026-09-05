package com.mc.pgs.lab2.pair.support;

import com.mc.pgs.lab2.processor.PaymentProcessorApplication;
import com.mc.pgs.lab2.tta.TtaApplication;
import org.springframework.boot.WebApplicationType;
import org.springframework.boot.builder.SpringApplicationBuilder;
import org.springframework.boot.web.servlet.context.ServletWebServerApplicationContext;
import org.springframework.context.ConfigurableApplicationContext;

/**
 * Starts each service in its own Spring context on its own random port, as two separately deployed
 * services would run. Nothing is shared but the HTTP call across the seam.
 *
 * <p>Two details are load-bearing, and both were found the hard way:
 * <ul>
 *   <li>Settings are passed as <em>command-line arguments</em>, not via
 *       {@code SpringApplicationBuilder.properties(..)}. The latter registers default properties,
 *       which rank <em>below</em> a config file, so a port set that way is silently overridden by
 *       the service's own configuration.</li>
 *   <li>Each service is pinned to its own {@code spring.config.name}. Both services are on this
 *       harness's classpath at once, and two {@code application.yml} files at the classpath root
 *       do not merge — one wins and the other service starts misconfigured.</li>
 * </ul>
 */
public final class ServiceLauncher implements AutoCloseable {

    private final ConfigurableApplicationContext context;
    private final int port;

    private ServiceLauncher(ConfigurableApplicationContext context) {
        this.context = context;
        this.port = ((ServletWebServerApplicationContext) context).getWebServer().getPort();
    }

    public static ServiceLauncher startProcessor() {
        return new ServiceLauncher(new SpringApplicationBuilder(PaymentProcessorApplication.class)
                .web(WebApplicationType.SERVLET)
                .run("--spring.config.name=" + PaymentProcessorApplication.CONFIG_NAME,
                     "--server.port=0",
                     "--spring.main.banner-mode=off"));
    }

    public static ServiceLauncher startTta(String processorBaseUrl) {
        return new ServiceLauncher(new SpringApplicationBuilder(TtaApplication.class)
                .web(WebApplicationType.SERVLET)
                .run("--spring.config.name=" + TtaApplication.CONFIG_NAME,
                     "--server.port=0",
                     "--spring.main.banner-mode=off",
                     "--processor.base-url=" + processorBaseUrl,
                     "--processor.card-payment-gateway-id=CP-1"));
    }

    public int port() {
        return port;
    }

    public String baseUrl() {
        return "http://localhost:" + port;
    }

    @Override
    public void close() {
        context.close();
    }
}
