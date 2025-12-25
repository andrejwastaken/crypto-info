package mk.ukim.finki.das.cryptoinfo.repository;

import mk.ukim.finki.das.cryptoinfo.model.TechnicalAnalysis;
import mk.ukim.finki.das.cryptoinfo.model.TechnicalAnalysisTimePeriod;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

@Repository
public interface TechnicalAnalysisRepository extends JpaRepository<TechnicalAnalysis, Long> {
    @Query("SELECT ta.normalizedScore FROM TechnicalAnalysis ta WHERE ta.symbol = :symbol AND ta.period = :period")
    Double findNormalizedScoreBySymbolAndPeriod(String symbol, TechnicalAnalysisTimePeriod period);
}
