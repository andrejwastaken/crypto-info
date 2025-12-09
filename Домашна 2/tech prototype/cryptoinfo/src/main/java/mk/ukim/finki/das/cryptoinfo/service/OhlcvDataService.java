package mk.ukim.finki.das.cryptoinfo.service;

import java.time.LocalDate;

import mk.ukim.finki.das.cryptoinfo.model.LowHigh;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import mk.ukim.finki.das.cryptoinfo.dto.CoinStatsDTO;
import mk.ukim.finki.das.cryptoinfo.model.OhlcvData;
import mk.ukim.finki.das.cryptoinfo.repository.OhlcvDataRepository;

@Service
public class OhlcvDataService {
    private final OhlcvDataRepository repository;

    public OhlcvDataService(OhlcvDataRepository repository) {
        this.repository = repository;
    }

    public OhlcvData getDataForSymbol(String symbol){
        return repository.findFirstBySymbolOrderByDateDesc(symbol);
    }

    public Page<OhlcvData> getDataForSymbol(String symbol, Pageable pageable){
        return repository.findBySymbol(symbol, pageable);
    }

    public Page<OhlcvData> getByDate(LocalDate date, Pageable pageable){
        return repository.findByDate(date, pageable);
    }
    
    public CoinStatsDTO getCoinStats(String symbol) {
        OhlcvData latest = repository.findLatestBySymbol(symbol);
        
        if (latest == null) {
            return null;
        }
        
        LowHigh lowHigh = repository.find52WeekLowHigh(symbol);

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
}
