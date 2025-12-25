package mk.ukim.finki.das.cryptoinfo.model;


import java.time.LocalDate;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Getter;
import org.hibernate.annotations.Immutable;

@Entity
@Getter
@Table(name = "ohlcv_data")
@Immutable
public class OhlcvData {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private Double close;
    private Double high;
    private Double low;
    private Double open;
    private Long volume;
    private LocalDate date;
    private String symbol;
    private String name;
}
