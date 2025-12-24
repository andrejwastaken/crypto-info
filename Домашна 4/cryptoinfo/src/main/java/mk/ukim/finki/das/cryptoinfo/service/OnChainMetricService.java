package mk.ukim.finki.das.cryptoinfo.service;

import mk.ukim.finki.das.cryptoinfo.model.OnChainMetric;
import mk.ukim.finki.das.cryptoinfo.repository.OnChainMetricRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class OnChainMetricService {
    private final OnChainMetricRepository repository;

    public OnChainMetricService(OnChainMetricRepository repository) {
        this.repository = repository;
    }

    public List<OnChainMetric> getOnChainForToday(){
        return repository.findTop4ByOrderByDateDesc();
    }
}
