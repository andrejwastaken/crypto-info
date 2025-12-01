package mk.ukim.finki.das.cryptoinfo.repository;

import java.time.LocalDate;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import mk.ukim.finki.das.cryptoinfo.model.OhlcvData;

public interface OhlcvDataRepository extends JpaRepository<OhlcvData, Long> {
    OhlcvData findFirstBySymbolOrderByDateDesc(String symbol);
    Page<OhlcvData> findBySymbol(String symbol, Pageable pageable);
    Page<OhlcvData> findByDate(LocalDate date, Pageable pageable);
    
    @Query("SELECT o FROM OhlcvData o WHERE o.symbol = :symbol ORDER BY o.date DESC LIMIT 1")
    OhlcvData findLatestBySymbol(@Param("symbol") String symbol);
    
    @Query("SELECT MIN(o.low), MAX(o.high) FROM OhlcvData o WHERE o.symbol = :symbol AND o.date >= CURRENT_DATE - 365")
    Object[] find52WeekLowHigh(@Param("symbol") String symbol);
}
