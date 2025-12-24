package mk.ukim.finki.das.cryptoinfo.repository;

import mk.ukim.finki.das.cryptoinfo.model.OnChainMetric;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface OnChainMetricRepository extends JpaRepository<OnChainMetric, Integer> {
    // todo: fix magic number
    List<OnChainMetric> findTop4ByOrderByDateDesc();
}
