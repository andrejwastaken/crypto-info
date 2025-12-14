package mk.ukim.finki.das.cryptoinfo.repository;

import mk.ukim.finki.das.cryptoinfo.model.OhlcvPrediction;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface OhlcvPredictionRepository extends JpaRepository<OhlcvPrediction, Integer> {
    OhlcvPrediction getOhlcvPredictionBySymbol(String symbol);
    List<OhlcvPrediction> findTop5ByOrderByPredictedChangePctDesc();
    List<OhlcvPrediction> findTop5ByOrderByPredictedChangePctAsc();
}
