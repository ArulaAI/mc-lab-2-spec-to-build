package com.mc.pgs.lab2.processor.repo;

import com.mc.pgs.lab2.processor.domain.OrderState;
import java.util.Optional;

public interface OrderStateRepository {

    Optional<OrderState> findByOrderId(String orderId);
}
