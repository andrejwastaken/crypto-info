package mk.ukim.finki.das.cryptoinfo.service;

import lombok.Getter;
import mk.ukim.finki.das.cryptoinfo.dto.JobStatus;
import mk.ukim.finki.das.cryptoinfo.dto.SentimentUpdateJob;
import mk.ukim.finki.das.cryptoinfo.exceptions.ServiceNotAvailableException;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ScheduledFuture;
import java.util.concurrent.TimeUnit;


@Service
public class SentimentUpdateService {
    private static final long UPDATE_COOLDOWN_MINUTES = 10;
    private static final long JOB_TIMEOUT_MINUTES = 2;

    @Getter
    private SentimentUpdateJob currentJob = null;
    @Getter
    private LocalDateTime lastCompletedAt = null;
    private final RestTemplate restTemplate = new RestTemplate();
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);
    private ScheduledFuture<?> timeoutTask = null;
    @Getter
    private boolean lastJobFailed = false;

    public synchronized SentimentUpdateJob startOrGetUpdate()
            throws ServiceNotAvailableException {
        if (currentJob != null && currentJob.getStatus() == JobStatus.PROCESSING) {
            System.out.println("update already in progress: " + currentJob.getJobId());
            return currentJob;
        }

        // check if we are currently in the cooldown period
        if (lastCompletedAt != null) {
            long minutesSinceLastUpdate = Duration.between(lastCompletedAt, LocalDateTime.now()).toMinutes();
            if (minutesSinceLastUpdate < UPDATE_COOLDOWN_MINUTES) {
                long minutesRemaining = UPDATE_COOLDOWN_MINUTES - minutesSinceLastUpdate;
                System.out.println("update attempted too soon. " + minutesRemaining + " minutes remaining");
                return null;
            }
        }

        // start new update

        UUID jobId = UUID.randomUUID();

        try {
            // todo: replace localhost in prod
            String callbackUrl =
                    "http://localhost:8080/api/sentiment/callback/" + jobId;
            Map<String, String> request = Map.of("callbackUrl", callbackUrl);

            restTemplate.postForEntity(
                    "http://localhost:8000/api/update-sentiment",
                    request,
                    String.class
            );
            currentJob = new SentimentUpdateJob(jobId, JobStatus.PROCESSING, LocalDateTime.now());
            lastJobFailed = false;
            System.out.println("Triggered update microservice.");

            scheduleTimeout(jobId);

            return currentJob;
        } catch (Exception e) {
            System.out.println("failed to trigger update. error: " + e);
                throw new ServiceNotAvailableException("Sentiment update service not available", e);
        }
    }

    private void scheduleTimeout(UUID jobId) {
        if (timeoutTask != null && !timeoutTask.isDone()){
            timeoutTask.cancel(false);
        }

        timeoutTask = scheduler.schedule(() -> {
            handleJobTimeout(jobId);
        }, JOB_TIMEOUT_MINUTES, TimeUnit.MINUTES);
    }

    private synchronized void handleJobTimeout(UUID jobId){
        if (currentJob != null && currentJob.getJobId().equals(jobId)
                && currentJob.getStatus() == JobStatus.PROCESSING) {
            System.out.println("Job timed out: " + jobId);
            currentJob = null;
            lastJobFailed = true;
        }
    }

    public synchronized void completeUpdate(UUID jobId, boolean failed) {
        if (currentJob == null || !currentJob.getJobId().equals(jobId)) {
            System.out.println("Invalid jobId:" + jobId);
            return;
        }

        if (timeoutTask != null && !timeoutTask.isDone()){
            timeoutTask.cancel(false);
        }

        if (!failed){
            System.out.println("update completed for jobId: " + jobId);
            lastCompletedAt = LocalDateTime.now();
            lastJobFailed = false;
        } else {
            System.out.println("update failed for jobId: " + jobId);
            lastJobFailed = true;
        }
        currentJob = null;
    }

    public Long getMinutesUntilNextUpdate() {
        if (lastCompletedAt == null) {
            return 0L;
        }
        long minutesSinceLastUpdate = Duration.between(lastCompletedAt, LocalDateTime.now()).toMinutes();
        long minutesRemaining = UPDATE_COOLDOWN_MINUTES - minutesSinceLastUpdate;
        return Math.max(0, minutesRemaining);
    }
}

