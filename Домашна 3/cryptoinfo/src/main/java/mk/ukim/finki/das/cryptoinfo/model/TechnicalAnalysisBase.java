package mk.ukim.finki.das.cryptoinfo.model;

import jakarta.persistence.Column;
import jakarta.persistence.Id;
import jakarta.persistence.MappedSuperclass;

@MappedSuperclass
public class TechnicalAnalysisBase {
    @Id
    private Long id;
    String symbol;
    @Column(name = "normalized_score")
    Double normalizedScore;
    String target;
}
