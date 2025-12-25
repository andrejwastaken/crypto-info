package mk.ukim.finki.das.cryptoinfo.service;

import lombok.RequiredArgsConstructor;
import mk.ukim.finki.das.cryptoinfo.dto.ExtremesDTO;
import mk.ukim.finki.das.cryptoinfo.model.OhlcvPrediction;
import mk.ukim.finki.das.cryptoinfo.repository.OhlcvPredictionRepository;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class OhlcvPredictionService {
    private final OhlcvPredictionRepository ohlcvPredictionRepository;

    public OhlcvPrediction getPredictionForSymbol(String symbol){
        return ohlcvPredictionRepository.getOhlcvPredictionBySymbol(symbol);
    }

    public ExtremesDTO getTopAndBottom5ByPercentageChange(){
        return new ExtremesDTO(
                ohlcvPredictionRepository.findTop5ByOrderByPredictedChangePctDesc(),
                ohlcvPredictionRepository.findTop5ByOrderByPredictedChangePctAsc()
        );
    }
}
