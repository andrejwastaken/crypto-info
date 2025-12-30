package mk.ukim.finki.das.cryptoinfo.config;

import lombok.Getter;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;

@Configuration
@Getter
public class SentimentServiceConfig {
    @Value("${sentiment.service.allowed-host}")
    private String allowedHost;

    @Value("${sentiment.service.secret-token}")
    private String secretToken;

    @Value("${sentiment.service.url}")
    private String serviceUrl;
}