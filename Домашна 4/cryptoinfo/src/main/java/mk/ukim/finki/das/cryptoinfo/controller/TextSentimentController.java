package mk.ukim.finki.das.cryptoinfo.controller;

import java.util.Map;
import java.util.UUID;

import lombok.RequiredArgsConstructor;
import mk.ukim.finki.das.cryptoinfo.config.SentimentServiceConfig;
import mk.ukim.finki.das.cryptoinfo.dto.CallbackRequest;
import mk.ukim.finki.das.cryptoinfo.dto.SentimentUpdateJob;
import mk.ukim.finki.das.cryptoinfo.exceptions.ServiceNotAvailableException;
import mk.ukim.finki.das.cryptoinfo.service.SentimentUpdateService;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.web.PagedResourcesAssembler;
import org.springframework.hateoas.EntityModel;
import org.springframework.hateoas.PagedModel;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import mk.ukim.finki.das.cryptoinfo.model.TextSentiment;
import mk.ukim.finki.das.cryptoinfo.service.TextSentimentService;

@RestController
@CrossOrigin(origins="*")
@RequestMapping("/api/sentiment")
@RequiredArgsConstructor
public class TextSentimentController {
    private final TextSentimentService textSentimentService;
    private final SentimentUpdateService sentimentUpdateService;
    @SuppressWarnings("SpringJavaInjectionPointsAutowiringInspection")
    private final PagedResourcesAssembler<TextSentiment> assembler;
    private final SentimentServiceConfig sentimentServiceConfig;

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
        try {
            SentimentUpdateJob job = sentimentUpdateService.startOrGetUpdate();
            if (job == null) {
                Long minutesRemaining = sentimentUpdateService.getMinutesUntilNextUpdate();
                return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS)
                        .body(Map.of(
                                "message", "Update requested too soon",
                                "minutesUntilNextUpdate", minutesRemaining
                        ));
            }
        } catch (ServiceNotAvailableException e) {
            return ResponseEntity.internalServerError().build();
        }

        return ResponseEntity.accepted().build();
    }

    @PostMapping("/callback/{jobId}")
    public ResponseEntity<Void> handleCallback(
            @PathVariable UUID jobId,
            @RequestBody CallbackRequest callbackRequest,
            @RequestHeader(value = "X-Secret-Token", required = false) String token
    ){
        if (token == null || !token.equals(sentimentServiceConfig.getSecretToken())){
            return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
        }
        boolean failed = callbackRequest.success() == null || !callbackRequest.success();
        sentimentUpdateService.completeUpdate(jobId, failed);
        return ResponseEntity.ok().build();
    }

    @GetMapping("/status")
    public ResponseEntity<Map<String, Object>> getStatus(){
        SentimentUpdateJob currentJob = sentimentUpdateService.getCurrentJob();

        if (currentJob == null){
            if (sentimentUpdateService.isLastJobFailed()){
                return ResponseEntity.ok(Map.of(
                        "status", "failed",
                        "message", "Last update job timed out"
                ));
            }

            if (sentimentUpdateService.getLastCompletedAt() != null){
                return ResponseEntity.ok(Map.of(
                        "status", "idle",
                        "lastCompletedAt", sentimentUpdateService.getLastCompletedAt(),
                        "minutesUntilNextUpdate", sentimentUpdateService.getMinutesUntilNextUpdate()
                ));
            }

            return ResponseEntity.ok(Map.of("status", "idle"));
        }

        return ResponseEntity.ok(Map.of(
                "status", currentJob.getStatus(),
                "startedAt", currentJob.getStartedAt()
        ));
    }
}
