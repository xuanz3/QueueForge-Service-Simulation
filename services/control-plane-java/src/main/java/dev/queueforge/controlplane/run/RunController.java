package dev.queueforge.controlplane.run;

import jakarta.validation.Valid;
import java.net.URI;
import java.util.List;
import java.util.UUID;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import tools.jackson.databind.json.JsonMapper;

@RestController
@RequestMapping("/api/runs")
public class RunController {
    private final RunService service;
    private final JsonMapper jsonMapper;

    public RunController(RunService service, JsonMapper jsonMapper) {
        this.service = service;
        this.jsonMapper = jsonMapper;
    }

    @PostMapping
    public ResponseEntity<RunResponse> create(@Valid @RequestBody CreateRunRequest request) {
        RunRecord run = service.submit(request);
        return ResponseEntity.accepted()
                .location(URI.create("/api/runs/" + run.id()))
                .body(RunResponse.from(run));
    }

    @GetMapping
    public List<RunResponse> list(@RequestParam(defaultValue = "50") int limit) {
        return service.list(limit).stream().map(RunResponse::from).toList();
    }

    @GetMapping("/{id}")
    public RunResponse get(@PathVariable UUID id) {
        return RunResponse.from(service.get(id));
    }

    @GetMapping("/{id}/result")
    public Object result(@PathVariable UUID id) {
        try {
            return jsonMapper.readValue(service.result(id), Object.class);
        } catch (Exception exception) {
            throw new RunConflictException("Stored run result is not valid JSON");
        }
    }

    @PostMapping("/{id}/cancel")
    public ResponseEntity<RunResponse> cancel(@PathVariable UUID id) {
        return ResponseEntity.accepted().body(RunResponse.from(service.cancel(id)));
    }
}
