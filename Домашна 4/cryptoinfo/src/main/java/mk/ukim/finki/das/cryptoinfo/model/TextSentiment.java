package mk.ukim.finki.das.cryptoinfo.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;
import lombok.Getter;

import java.time.LocalDate;
import java.util.List;

@Entity
@Table(name = "news_sentiment")
@Getter
public class TextSentiment {
    @Id
    private Long id;

    @NotNull
    private String title;

    private LocalDate date;

    @Column(columnDefinition = "text[]")
    private String[] symbols;

    private String link;

    @Column(name = "img_src")
    private String ImageLink;

    @Column(name = "sentiment_label")
    private String label;

    @Column(name = "sentiment_score")
    private Float score;

}
