package mk.ukim.finki.das.cryptoinfo.repository;

import mk.ukim.finki.das.cryptoinfo.model.OnChainSentimentPrediction;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface OnChainSentimentPredictionRepository extends JpaRepository<OnChainSentimentPrediction, Integer> {
}
