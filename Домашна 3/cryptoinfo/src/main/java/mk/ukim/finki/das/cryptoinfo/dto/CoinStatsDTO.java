package mk.ukim.finki.das.cryptoinfo.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class CoinStatsDTO {
    // 24h data (latest day)
    private Double low24h;
    private Double high24h;
    private Long volume24h;
    private Double open;
    private Double close;
    
    // 52 week data
    private Double low52w;
    private Double high52w;
    
    // coin info
    private String symbol;
    private String name;
}
