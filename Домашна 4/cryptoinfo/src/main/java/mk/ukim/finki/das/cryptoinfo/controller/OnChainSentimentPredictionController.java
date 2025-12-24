package mk.ukim.finki.das.cryptoinfo.controller;

import mk.ukim.finki.das.cryptoinfo.model.OnChainSentimentPrediction;
import mk.ukim.finki.das.cryptoinfo.service.OnChainSentimentPredictionService;
import org.springframework.http.HttpEntity;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@CrossOrigin(origins = "*")
@RequestMapping("/api/chain-sentiment-prediction")
public class OnChainSentimentPredictionController {
    private final OnChainSentimentPredictionService predictionService;

    public OnChainSentimentPredictionController(OnChainSentimentPredictionService predictionService) {
        this.predictionService = predictionService;
    }

    @GetMapping
    public HttpEntity<List<OnChainSentimentPrediction>> getPredictions(){
        return ResponseEntity.ok(predictionService.getAllPredictions());
    }
}
