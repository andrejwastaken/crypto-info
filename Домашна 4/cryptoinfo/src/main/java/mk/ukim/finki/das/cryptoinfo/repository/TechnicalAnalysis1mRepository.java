package mk.ukim.finki.das.cryptoinfo.repository;

import mk.ukim.finki.das.cryptoinfo.model.TechnicalAnalysis1m;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

@Repository
public interface TechnicalAnalysis1mRepository extends JpaRepository<TechnicalAnalysis1m, Long> {
    @Query("select ta.normalizedScore from TechnicalAnalysis1m ta where ta.symbol = :symbol")
    Double findNormalizedScoreBySymbol(String symbol);
}

