package mk.ukim.finki.das.cryptoinfo.repository;

import mk.ukim.finki.das.cryptoinfo.model.TextSentiment;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface TextSentimentRepository extends JpaRepository<TextSentiment, Long> {
    @Query(value = """
    select * 
    from news_sentiment 
    ORDER BY
        CASE
            WHEN CAST(:symbol AS text) = ANY(symbols) THEN 0
            ELSE 1
        END,
        id 
    """,
            nativeQuery = true)
    List<TextSentiment> findTopBySymbolPriority(@Param("symbol") String symbol);
}
