package mk.ukim.finki.das.cryptoinfo.service;

import mk.ukim.finki.das.cryptoinfo.dto.ExtremesDto;
import mk.ukim.finki.das.cryptoinfo.model.OhlcvPrediction;
import mk.ukim.finki.das.cryptoinfo.repository.OhlcvPredictionRepository;
import org.springframework.stereotype.Service;

@Service
public class OhlcvPredictionService {
    private final OhlcvPredictionRepository ohlcvPredictionRepository;

    public OhlcvPredictionService(OhlcvPredictionRepository ohlcvPredictionRepository) {
        this.ohlcvPredictionRepository = ohlcvPredictionRepository;
    }

    public OhlcvPrediction getPredictionForSymbol(String symbol){
        return ohlcvPredictionRepository.getOhlcvPredictionBySymbol(symbol);
    }

    public ExtremesDto getTopAndBottom5ByPercentageChange(){
        return new ExtremesDto(
                ohlcvPredictionRepository.findTop5ByOrderByPredictedChangePctDesc(),
                ohlcvPredictionRepository.findTop5ByOrderByPredictedChangePctAsc()
        );
    }
}
