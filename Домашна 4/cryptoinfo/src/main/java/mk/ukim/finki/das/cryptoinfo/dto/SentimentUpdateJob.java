package mk.ukim.finki.das.cryptoinfo.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.io.Serializable;
import java.time.LocalDateTime;
import java.util.UUID;

@AllArgsConstructor
@Data
public class SentimentUpdateJob implements Serializable {
    private UUID jobId;
    private JobStatus status;
    private LocalDateTime startedAt;

}
