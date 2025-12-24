package mk.ukim.finki.das.cryptoinfo.service;

import java.util.List;

import org.springframework.stereotype.Service;

import mk.ukim.finki.das.cryptoinfo.model.OnChainSentimentPrediction;
import mk.ukim.finki.das.cryptoinfo.repository.OnChainSentimentPredictionRepository;

@Service
public class OnChainSentimentPredictionService {
    private final OnChainSentimentPredictionRepository repository;

    public OnChainSentimentPredictionService(OnChainSentimentPredictionRepository repository) {
        this.repository = repository;
    }

    public List<OnChainSentimentPrediction> getAllPredictions(){
        return repository.findAll();
    }
}
