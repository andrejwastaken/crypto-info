package mk.ukim.finki.das.cryptoinfo.service;

import lombok.Getter;
import mk.ukim.finki.das.cryptoinfo.dto.JobStatus;
import mk.ukim.finki.das.cryptoinfo.dto.SentimentUpdateJob;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class SentimentUpdateService {
    @Getter
    private SentimentUpdateJob currentJob = null;
    private final Set<SseEmitter> emitters = ConcurrentHashMap.newKeySet();
    private final RestTemplate restTemplate = new RestTemplate();

    public synchronized SentimentUpdateJob startOrGetUpdate() {
        if (currentJob != null && currentJob.getStatus() == JobStatus.PROCESSING) {
            System.out.println("update already in progress: " + currentJob.getJobId());
            return currentJob;
        }

        UUID jobId = UUID.randomUUID();
        currentJob = new SentimentUpdateJob(jobId, JobStatus.PROCESSING, LocalDateTime.now());

        CompletableFuture.runAsync(() -> {
            try {
                // replace in prod
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
                completeUpdate(jobId, true);
            }
        });
        return currentJob;
    }

    public void registerEmitter(SseEmitter emitter){
        emitters.add(emitter);

        Runnable cleanup = () -> {
            emitters.remove(emitter);
            System.out.println("removed emitter, active emitters left: " + emitters.size());
        };

        emitter.onCompletion(cleanup);
        emitter.onTimeout(cleanup);
        emitter.onError(e -> cleanup.run());

        System.out.println("registered emitter, active emitters: " + emitters.size());
    }

    public synchronized void completeUpdate(UUID jobId, boolean error){
        if (currentJob == null || !currentJob.getJobId().equals(jobId)) {
            System.out.println("Invalid jobId:" + jobId);
            return;
        }

        currentJob.setStatus(JobStatus.COMPLETED);
        System.out.println("update completed for jobId: " + jobId);

        // notify all clients
        Map<String, Object> completionMessage = Map.of(
                "status", JobStatus.COMPLETED,
                "jobId", jobId,
                "error", error
        );

        List<SseEmitter> deadEmitters = new ArrayList<>();
        for (SseEmitter emitter : emitters){
            try {
                emitter.send(SseEmitter.event()
                        .name("update-complete")
                        .data(completionMessage));
                emitter.complete();
            } catch (IOException e) {
                System.out.println("failed to send completion to emitter. error: " + e);
                deadEmitters.add(emitter);
            }
        }

        deadEmitters.forEach(emitters::remove);
        System.out.println("notified clients of completion");
        currentJob = null;
    }

}

