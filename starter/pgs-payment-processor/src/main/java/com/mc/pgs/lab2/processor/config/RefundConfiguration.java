package com.mc.pgs.lab2.processor.config;

import com.mc.pgs.lab2.processor.domain.CaptureState;
import com.mc.pgs.lab2.processor.domain.OrderState;
import com.mc.pgs.lab2.processor.repo.InMemoryOrderStateRepository;
import com.mc.pgs.lab2.processor.repo.OrderStateRepository;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

@Configuration
@EnableConfigurationProperties(RefundProperties.class)
public class RefundConfiguration {

    @Bean
    public OrderStateRepository orderStateRepository(RefundProperties properties) {
        List<OrderState> seed = properties.orders() == null ? List.of()
                : properties.orders().stream()
                    .map(o -> new OrderState(o.orderId(), o.currency(), o.totalCapturedAmount(),
                            o.captures() == null ? List.of()
                                    : o.captures().stream()
                                        .map(c -> new CaptureState(c.captureTransactionId(), c.amount()))
                                        .toList()))
                    .toList();
        return new InMemoryOrderStateRepository(seed);
    }
}
