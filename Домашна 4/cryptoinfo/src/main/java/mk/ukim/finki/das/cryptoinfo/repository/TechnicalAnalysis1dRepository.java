package mk.ukim.finki.das.cryptoinfo.repository;

import mk.ukim.finki.das.cryptoinfo.model.TechnicalAnalysis1d;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

@Repository
public interface TechnicalAnalysis1dRepository extends JpaRepository<TechnicalAnalysis1d, Long> {
    @Query("select ta.normalizedScore from TechnicalAnalysis1d ta where ta.symbol = :symbol")
    Double findNormalizedScoreBySymbol(String symbol);
}

