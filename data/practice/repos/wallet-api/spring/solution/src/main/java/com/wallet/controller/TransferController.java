package com.wallet.controller;

import com.wallet.service.TransferService;
import java.util.Map;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
public class TransferController {
    private final TransferService transfers;

    public TransferController(TransferService transfers) {
        this.transfers = transfers;
    }

    /** POST /api/transfers  {from, to, amount, at?} */
    @PostMapping("/transfers")
    public ResponseEntity<Map<String, Object>> createTransfer(@RequestBody(required = false) Map<String, Object> body) {
        return ResponseEntity.status(201).body(transfers.transfer(Bodies.text(body, "from"), Bodies.text(body, "to"),
                Bodies.value(body, "amount"), Bodies.time(body)));
    }
}
