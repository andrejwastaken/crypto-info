package mk.ukim.finki.das.cryptoinfo.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import org.hibernate.annotations.Immutable;

import java.math.BigDecimal;
import java.time.LocalDate;

@Entity
@Table(name = "onchain_metrics")
@Getter
@Immutable
public class OnChainMetric {
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

    @Column(name = "active_addresses")
    private Long activeAddresses;

    @Column(name = "transactions")
    private Long transactions;

    @Column(name = "exchange_inflow")
    private BigDecimal exchangeInflow;

    @Column(name = "exchange_outflow")
    private BigDecimal exchangeOutflow;

    @Column(name = "whale_transactions")
    private BigDecimal whaleTransactions;

    @Column(name = "nvt_ratio")
    private BigDecimal nvtRatio;

    @Column(name = "mvrv_ratio")
    private BigDecimal mvrvRatio;

    @Column(name = "net_flow")
    private BigDecimal netFlow;

    @Column(name = "security_value")
    private BigDecimal securityValue;

    @Column(name = "tvl_usd")
    private Long tvlUsd;
}
