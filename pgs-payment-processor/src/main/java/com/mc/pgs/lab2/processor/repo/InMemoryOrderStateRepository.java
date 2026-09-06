package com.mc.pgs.lab2.processor.repo;

import com.mc.pgs.lab2.processor.domain.OrderState;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * Lab representation of stored order state. Seeded from externalised configuration rather than
 * hardcoded, so the fixture is visible and changeable without touching source.
 */
public class InMemoryOrderStateRepository implements OrderStateRepository {

    private final Map<String, OrderState> byOrderId = new LinkedHashMap<>();

    public InMemoryOrderStateRepository(List<OrderState> seed) {
        seed.forEach(o -> byOrderId.put(o.orderId(), o));
    }

    @Override
    public Optional<OrderState> findByOrderId(String orderId) {
        return Optional.ofNullable(byOrderId.get(orderId));
    }
}
