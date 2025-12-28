package mk.ukim.finki.das.cryptoinfo.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;
import lombok.Getter;
import org.hibernate.annotations.Immutable;

import java.time.LocalDateTime;

@Entity
@Table(name = "news_sentiment")
@Getter
@Immutable
public class TextSentiment {
    @Id
    private Long id;

    @NotNull
    private String title;

    private LocalDateTime date;

    @Column(columnDefinition = "text[]")
    @SuppressWarnings("JpaAttributeTypeInspection")
    private String[] symbols;

    private String link;

    @Column(name = "img_src")
    private String ImageLink;

    @Column(name = "sentiment_label")
    private String label;

    @Column(name = "sentiment_score")
    private Float score;

}
