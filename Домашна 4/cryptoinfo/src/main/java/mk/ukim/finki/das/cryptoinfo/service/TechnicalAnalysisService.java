package mk.ukim.finki.das.cryptoinfo.service;

import lombok.RequiredArgsConstructor;
import mk.ukim.finki.das.cryptoinfo.model.TechnicalAnalysis;
import mk.ukim.finki.das.cryptoinfo.model.TechnicalAnalysisTimePeriod;
import mk.ukim.finki.das.cryptoinfo.repository.TechnicalAnalysisRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class TechnicalAnalysisService {
    private final TechnicalAnalysisRepository repository;

    public Double getScoreForSymbol(String symbol, TechnicalAnalysisTimePeriod timePeriod){
        return repository.findNormalizedScoreBySymbolAndPeriod(symbol, timePeriod);
    }

    public List<TechnicalAnalysis> getStatsForSymbol(String symbol){
        return repository.getBySymbol(symbol);
    }

}
