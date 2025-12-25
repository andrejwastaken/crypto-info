package mk.ukim.finki.das.cryptoinfo.repository;

import mk.ukim.finki.das.cryptoinfo.model.OnChainMetric;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;

@Repository
public interface OnChainMetricRepository extends JpaRepository<OnChainMetric, Integer> {
    @Query("select max(o.date) from OnChainMetric o")
    LocalDate findMaxDate();

    List<OnChainMetric> findByDate(LocalDate date);
}
