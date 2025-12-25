package mk.ukim.finki.das.cryptoinfo.service;

import java.util.List;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import mk.ukim.finki.das.cryptoinfo.model.OnChainSentimentPrediction;
import mk.ukim.finki.das.cryptoinfo.repository.OnChainSentimentPredictionRepository;

@Service
@RequiredArgsConstructor
public class OnChainSentimentPredictionService {
    private final OnChainSentimentPredictionRepository repository;

    public List<OnChainSentimentPrediction> getAllPredictions(){
        return repository.findAll();
    }
}
