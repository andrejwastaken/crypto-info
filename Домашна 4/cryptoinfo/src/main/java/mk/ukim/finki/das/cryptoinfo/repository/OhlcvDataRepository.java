package mk.ukim.finki.das.cryptoinfo.repository;

import mk.ukim.finki.das.cryptoinfo.model.CoinPctChangeProjection;
import mk.ukim.finki.das.cryptoinfo.model.LowHighProjection;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import mk.ukim.finki.das.cryptoinfo.model.OhlcvData;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface OhlcvDataRepository extends JpaRepository<OhlcvData, Long> {
    Page<OhlcvData> findBySymbol(String symbol, Pageable pageable);

    @Query("SELECT o FROM OhlcvData o WHERE o.symbol = :symbol ORDER BY o.date DESC LIMIT 1")
    OhlcvData findLatestBySymbol(@Param("symbol") String symbol);

    @Query(value = """
    SELECT MIN(low) as low, MAX(high) as high
    FROM ohlcv_data
    WHERE symbol = :symbol
    AND date >= CURRENT_DATE - INTERVAL '365 days'
    """, nativeQuery = true)
    LowHighProjection find52WeekLowHigh(@Param("symbol") String symbol);

    // not optimized:)
    @Query(value = """
    WITH top_coins AS (
            SELECT
                symbol,
                ROW_NUMBER() OVER (ORDER BY market_cap DESC) as rank
            FROM coins_metadata
            ORDER BY market_cap DESC
            LIMIT 15
        ),
        latest_dates AS (
            SELECT
                MAX(date) as latest_date,
                MAX(date) - 1 as previous_date
            FROM ohlcv_data
        ),
        price_data AS (
            SELECT
                o.symbol,
                o.date,
                o.close,
                tc.rank
            FROM ohlcv_data o
            JOIN top_coins tc ON o.symbol = tc.symbol
            CROSS JOIN latest_dates ld
            WHERE o.date IN (ld.latest_date, ld.previous_date)
        )
        SELECT
            symbol,
            ((MAX(CASE WHEN date = (SELECT latest_date FROM latest_dates) THEN close END) -
              MAX(CASE WHEN date = (SELECT previous_date FROM latest_dates) THEN close END)) /
             MAX(CASE WHEN date = (SELECT previous_date FROM latest_dates) THEN close END)) * 100
            AS pctChange
        FROM price_data
        GROUP BY symbol, rank
        ORDER BY rank
    """, nativeQuery = true)
    List<CoinPctChangeProjection> getTopCoinsWithPctChange();
}
