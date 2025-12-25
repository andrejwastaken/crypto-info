package mk.ukim.finki.das.cryptoinfo.model;

import jakarta.persistence.*;
import org.hibernate.annotations.Immutable;

import java.time.LocalDate;

@Entity
@Table(name = "technical_analysis")
@Immutable
public class TechnicalAnalysis {
    @Id
    @Column(name = "id")
    private Long id;

    @Column(name = "date")
    private LocalDate date;

    @Column(name = "osc_rsi")
    private Double rsi;

    @Column(name = "osc_macd_line")
    private Double macdLine;

    @Column(name = "osc_macd_signal")
    private Double macdSignal;

    @Column(name = "osc_stoch_k")
    private Double stochK;

    @Column(name = "osc_stoch_d")
    private Double stochD;

    @Column(name = "osc_dmi_plus")
    private Double dmiPlus;

    @Column(name = "osc_dmi_minus")
    private Double dmiMinus;

    @Column(name = "osc_adx")
    private Double adx;

    @Column(name = "osc_cci")
    private Double cci;

    @Column(name = "symbol", length = Integer.MAX_VALUE)
    private String symbol;

    @Column(name = "ma_sma")
    private Double sma;

    @Column(name = "ma_ema")
    private Double ema;

    @Column(name = "ma_wma")
    private Double wma;

    @Column(name = "ma_bollinger_middle")
    private Double bollingerMiddle;

    @Column(name = "ma_volume_sma")
    private Double volumeSma;

    @Column(name = "normalized_score")
    private Double normalizedScore;

    @Column(name = "period")
    @Enumerated(value = EnumType.STRING)
    private TechnicalAnalysisTimePeriod period;


}
