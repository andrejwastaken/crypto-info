package mk.ukim.finki.das.cryptoinfo.controller;

import lombok.RequiredArgsConstructor;
import mk.ukim.finki.das.cryptoinfo.model.OnChainMetric;
import mk.ukim.finki.das.cryptoinfo.service.OnChainMetricService;
import org.springframework.http.HttpEntity;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@CrossOrigin(origins = "*")
@RequestMapping("/api/on-chain")
@RequiredArgsConstructor
public class OnChainMetricController {
    private final OnChainMetricService onChainMetricService;

    @GetMapping
    public HttpEntity<List<OnChainMetric>> getOnChainForToday(){
        return ResponseEntity.ok(onChainMetricService.getOnChainForToday());
    }
}