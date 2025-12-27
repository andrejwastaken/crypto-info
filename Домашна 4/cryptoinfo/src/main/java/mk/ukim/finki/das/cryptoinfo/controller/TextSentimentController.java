package mk.ukim.finki.das.cryptoinfo.controller;

import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;

import lombok.RequiredArgsConstructor;
import mk.ukim.finki.das.cryptoinfo.dto.SentimentUpdateJob;
import mk.ukim.finki.das.cryptoinfo.service.SentimentUpdateService;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.web.PagedResourcesAssembler;
import org.springframework.hateoas.EntityModel;
import org.springframework.hateoas.PagedModel;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import mk.ukim.finki.das.cryptoinfo.model.TextSentiment;
import mk.ukim.finki.das.cryptoinfo.service.TextSentimentService;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

@RestController
@CrossOrigin(origins="*")
@RequestMapping("/api/sentiment")
@RequiredArgsConstructor
public class TextSentimentController {
    private final TextSentimentService textSentimentService;
    private final SentimentUpdateService sentimentUpdateService;
    @SuppressWarnings("SpringJavaInjectionPointsAutowiringInspection")
    private final PagedResourcesAssembler<TextSentiment> assembler;

    @GetMapping
    public PagedModel<EntityModel<TextSentiment>> getNewsBySymbol(
            @RequestParam String symbol,
            Pageable pageable
    ){
        Page<TextSentiment> page = textSentimentService.getNewsBySymbol(symbol, pageable);
        return assembler.toModel(page);
    }

    @PostMapping("/update")
    public ResponseEntity<Map<String, Object>> triggerUpdate(){
        SentimentUpdateJob job = sentimentUpdateService.startOrGetUpdate();

        return ResponseEntity.accepted()
                .body(Map.of(
                        "jobId", job.getJobId(),
                        "status", job.getStatus(),
                        "streamUrl", "api/sentiment/stream"
                ));
    }

    @GetMapping("/stream")
    public SseEmitter streamUpdates(){
        SseEmitter emitter = new SseEmitter(10L * 60 * 1000); // 10 min timeout

        sentimentUpdateService.registerEmitter(emitter);
        SentimentUpdateJob currentJob = sentimentUpdateService.getCurrentJob();
        if (currentJob != null){
            try {
                emitter.send(SseEmitter.event()
                        .name("status")
                        .data(Map.of(
                                "status", currentJob.getStatus(),
                                "jobId", currentJob.getJobId()
                        )));
            } catch (IOException e){
                System.out.println("failed to send initial status. error: " + e);
                emitter.completeWithError(e);
            }
        }
        return emitter;
    }

    @PostMapping("/callback/{jobId}")
    public ResponseEntity<Void> handleCallback(@PathVariable UUID jobId){
        sentimentUpdateService.completeUpdate(jobId, false);
        return ResponseEntity.ok().build();
    }

    @GetMapping("/status")
    public ResponseEntity<Map<String, Object>> getStatus(){
        SentimentUpdateJob currentJob = sentimentUpdateService.getCurrentJob();

        if (currentJob == null){
            return ResponseEntity.ok(Map.of("status", "idle"));
        }

        return ResponseEntity.ok(Map.of(
                "status", currentJob.getStatus(),
                "jobId", currentJob.getJobId(),
                "startedAt", currentJob.getStartedAt()
        ));
    }
}
