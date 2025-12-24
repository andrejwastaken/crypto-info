package mk.ukim.finki.das.cryptoinfo.service;

import mk.ukim.finki.das.cryptoinfo.model.TechnicalAnalysisTimePeriod;
import mk.ukim.finki.das.cryptoinfo.repository.TechnicalAnalysis1dRepository;
import mk.ukim.finki.das.cryptoinfo.repository.TechnicalAnalysis1mRepository;
import mk.ukim.finki.das.cryptoinfo.repository.TechnicalAnalysis1wRepository;
import org.springframework.stereotype.Service;

@Service
public class TechnicalAnalysisService {
    private final TechnicalAnalysis1dRepository repository1d;
    private final TechnicalAnalysis1wRepository repository1w;
    private final TechnicalAnalysis1mRepository repository1m;

    public TechnicalAnalysisService(TechnicalAnalysis1dRepository repository1d, TechnicalAnalysis1wRepository repository1w, TechnicalAnalysis1mRepository repository1m) {
        this.repository1d = repository1d;
        this.repository1w = repository1w;
        this.repository1m = repository1m;
    }

    public Double getScoreForSymbol(String symbol, TechnicalAnalysisTimePeriod timePeriod){
        return switch (timePeriod) {
            case DAY -> repository1d.findNormalizedScoreBySymbol(symbol);
            case WEEK -> repository1w.findNormalizedScoreBySymbol(symbol);
            case MONTH -> repository1m.findNormalizedScoreBySymbol(symbol);
        };
    }

}
