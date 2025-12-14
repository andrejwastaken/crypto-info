package mk.ukim.finki.das.cryptoinfo.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Getter;

import java.math.BigDecimal;
import java.time.LocalDate;

@Entity
@Table(name = "ohlcv_predictions")
@Getter
public class OhlcvPrediction {
    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE)
    @Column(name = "id", nullable = false)
    private Integer id;

    @Size(max = 20)
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
