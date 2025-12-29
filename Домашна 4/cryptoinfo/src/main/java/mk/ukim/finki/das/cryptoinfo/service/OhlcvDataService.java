package mk.ukim.finki.das.cryptoinfo.service;

import lombok.RequiredArgsConstructor;
import mk.ukim.finki.das.cryptoinfo.model.CoinPctChangeProjection;
import mk.ukim.finki.das.cryptoinfo.model.LowHighProjection;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import mk.ukim.finki.das.cryptoinfo.dto.CoinStatsDTO;
import mk.ukim.finki.das.cryptoinfo.model.OhlcvData;
import mk.ukim.finki.das.cryptoinfo.repository.OhlcvDataRepository;

import java.util.List;

@Service
@RequiredArgsConstructor
public class OhlcvDataService {
    private final OhlcvDataRepository repository;

    public Page<OhlcvData> getDataForSymbol(String symbol, Pageable pageable){
        return repository.findBySymbol(symbol, pageable);
    }
    
    public CoinStatsDTO getCoinStats(String symbol) {
        OhlcvData latest = repository.findLatestBySymbol(symbol);
        
        if (latest == null) {
            return null;
        }
        
        LowHighProjection lowHigh = repository.find52WeekLowHigh(symbol);

        Double low52w = lowHigh != null && lowHigh.getLow() != null ? lowHigh.getLow() : null;
        Double high52w = lowHigh != null && lowHigh.getHigh() != null ? lowHigh.getHigh() : null;
        
        // latest -> 24h data; lowHigh -> 52w data

        return new CoinStatsDTO(
            latest.getLow(),     
            latest.getHigh(),    
            latest.getVolume(),  
            latest.getOpen(),    
            latest.getClose(),
            low52w,
            high52w,
            latest.getSymbol(),  
            latest.getName()     
        );
    }

    public List<CoinPctChangeProjection> getTopCoinsWithPctChange(){
        return repository.getTopCoinsWithPctChange();
    }
}
