package mk.ukim.finki.das.cryptoinfo.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;
import lombok.*;
import org.hibernate.annotations.Immutable;


import java.time.LocalDate;

@Entity
@Getter
@Table(name = "coins_metadata")
@Immutable
public class Coin {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String symbol;

    private String name;

    @Column(name = "updated_at", columnDefinition = "DATE")
    private LocalDate updatedAt;

    @Column(name = "market_cap")
    private Double marketCap;

    @Column(name = "circulating_supply")
    private Double circulatingSupply;

    private Double volume;

    @Column(name = "change_52w")
    private Double change52w;
}
