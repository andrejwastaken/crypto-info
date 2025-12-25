package mk.ukim.finki.das.cryptoinfo.service;

import lombok.RequiredArgsConstructor;
import mk.ukim.finki.das.cryptoinfo.model.OnChainMetric;
import mk.ukim.finki.das.cryptoinfo.repository.OnChainMetricRepository;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.List;

@Service
@RequiredArgsConstructor
public class OnChainMetricService {
    private final OnChainMetricRepository repository;

    public List<OnChainMetric> getOnChainForToday(){
        LocalDate date = repository.findMaxDate();
        return repository.findByDate(date);
    }
}
