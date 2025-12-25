package mk.ukim.finki.das.cryptoinfo.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import org.hibernate.annotations.Immutable;

import java.math.BigDecimal;
import java.time.LocalDate;

@Entity
@Table(name = "ohlcv_predictions")
@Immutable
public class OhlcvPrediction {
    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE)
    @Column(name = "id", nullable = false)
    private Integer id;

    @Size(max = 20)
    @NotNull
    @Column(name = "symbol", nullable = false, length = 20)
    @Getter
    private String symbol;

    @NotNull
    @Column(name = "date", nullable = false)
    private LocalDate date;

    @Column(name = "predicted_close")
    @Getter
    private BigDecimal predictedClose;

    @Column(name = "predicted_change_pct")
    @Getter
    private BigDecimal predictedChangePct;
}
