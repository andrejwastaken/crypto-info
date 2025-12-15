package mk.ukim.finki.das.cryptoinfo.model;

import java.math.BigDecimal;
import java.time.LocalDate;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.validation.constraints.NotNull;

@Entity
@Table(name = "on_chain_sentiment_predictions")
public class OnChainSentimentPrediction {
    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE)
    @Column(name = "id", nullable = false)
    private Integer id;

    @NotNull
    @Column(name = "symbol", nullable = false, length = 20)
    private String symbol;

    @NotNull
    @Column(name = "date", nullable = false)
    private LocalDate date;

    @Column(name = "predicted_close")
    private BigDecimal predictedClose;

    @Column(name = "predicted_change_pct")
    private BigDecimal predictedChangePct;
}
