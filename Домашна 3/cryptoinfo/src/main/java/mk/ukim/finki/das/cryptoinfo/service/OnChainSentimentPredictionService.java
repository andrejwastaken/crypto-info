package mk.ukim.finki.das.cryptoinfo.service;

import mk.ukim.finki.das.cryptoinfo.repository.OnChainSentimentPredictionRepository;
import org.springframework.stereotype.Service;

@Service
public class OnChainSentimentPredictionService {
    private final OnChainSentimentPredictionRepository repository;

    public OnChainSentimentPredictionService(OnChainSentimentPredictionRepository repository) {
        this.repository = repository;
    }

}
