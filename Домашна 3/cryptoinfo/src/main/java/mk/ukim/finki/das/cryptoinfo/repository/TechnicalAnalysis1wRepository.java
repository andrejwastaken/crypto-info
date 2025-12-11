package mk.ukim.finki.das.cryptoinfo.repository;

import mk.ukim.finki.das.cryptoinfo.model.TechnicalAnalysis1w;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

@Repository
public interface TechnicalAnalysis1wRepository extends JpaRepository<TechnicalAnalysis1w, Long> {
    @Query("select ta.normalizedScore from TechnicalAnalysis1w ta where ta.symbol = :symbol")
    Double findNormalizedScoreBySymbol(String symbol);
}

