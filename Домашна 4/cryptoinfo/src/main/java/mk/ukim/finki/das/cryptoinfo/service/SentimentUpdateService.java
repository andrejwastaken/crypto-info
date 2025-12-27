package mk.ukim.finki.das.cryptoinfo.service;

import lombok.Getter;
import mk.ukim.finki.das.cryptoinfo.dto.JobStatus;
import mk.ukim.finki.das.cryptoinfo.dto.SentimentUpdateJob;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.CompletableFuture;


@Service
public class SentimentUpdateService {
    private static final long UPDATE_COOLDOWN_MINUTES = 10;

    @Getter
    private SentimentUpdateJob currentJob = null;
    @Getter
    private LocalDateTime lastCompletedAt = null;
    private final RestTemplate restTemplate = new RestTemplate();

    public synchronized SentimentUpdateJob startOrGetUpdate() {
        if (currentJob != null && currentJob.getStatus() == JobStatus.PROCESSING) {
            System.out.println("update already in progress: " + currentJob.getJobId());
            return currentJob;
        }

        // check if we are currently in the cooldown period
        if (lastCompletedAt != null) {
            long minutesSinceLastUpdate = Duration.between(lastCompletedAt, LocalDateTime.now()).toMinutes();
            if (minutesSinceLastUpdate < UPDATE_COOLDOWN_MINUTES){
                long minutesRemaining = UPDATE_COOLDOWN_MINUTES - minutesSinceLastUpdate;
                System.out.println("update attempted too soon. " + minutesRemaining + " minutes remaining");
                return null;
            }
        }

        // start new update
        UUID jobId = UUID.randomUUID();
        currentJob = new SentimentUpdateJob(jobId, JobStatus.PROCESSING, LocalDateTime.now());

        CompletableFuture.runAsync(() -> {
            try {
                // todo: replace in prod
                String callbackUrl =
                        "http://localhost:8080/api/sentiment/callback/" + jobId;
                Map<String, String> request = Map.of("callbackUrl", callbackUrl);

                restTemplate.postForEntity(
                        "http://localhost:8000/api/test",
//                        "http://localhost:8000/api/update-sentiment",
                        request,
                        String.class
                );

                System.out.println("Triggered update microservice.");
            } catch (Exception e) {
                System.out.println("failed to trigger update. error: " + e);
                completeUpdate(jobId);
            }
        });
        return currentJob;
    }

    public synchronized void completeUpdate(UUID jobId){
        if (currentJob == null || !currentJob.getJobId().equals(jobId)) {
            System.out.println("Invalid jobId:" + jobId);
            return;
        }

        currentJob.setStatus(JobStatus.COMPLETED);
        lastCompletedAt = LocalDateTime.now();
        System.out.println("update completed for jobId: " + jobId);

        currentJob = null;
    }

    public Long getMinutesUntilNextUpdate(){
        if (lastCompletedAt == null){
            return 0L;
        }
        long minutesSinceLastUpdate = Duration.between(lastCompletedAt, LocalDateTime.now()).toMinutes();
        long minutesRemaining = UPDATE_COOLDOWN_MINUTES - minutesSinceLastUpdate;
        return Math.max(0, minutesRemaining);
    }



}

