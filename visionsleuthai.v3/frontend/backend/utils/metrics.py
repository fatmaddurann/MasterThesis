from prometheus_client import Counter, Histogram, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
import time

registry = CollectorRegistry()

frames_processed = Counter(
    'vs_frames_processed_total',
    'Total frames processed by live analysis',
    ['client_id'],
    registry=registry
)

frames_dropped = Counter(
    'vs_frames_dropped_total',
    'Total frames dropped due to rate limiting or lock',
    ['client_id', 'reason'],
    registry=registry
)

frame_latency_ms = Histogram(
    'vs_frame_processing_latency_ms',
    'Live frame processing latency in milliseconds',
    buckets=(5, 10, 20, 50, 100, 200, 400, 800, 1600, 3200),
    registry=registry
)

# Upload and analysis metrics
uploads_total = Counter(
    'vs_video_uploads_total',
    'Total number of video uploads',
    registry=registry
)

upload_failures_total = Counter(
    'vs_video_upload_failures_total',
    'Total number of failed video uploads',
    registry=registry
)

analysis_jobs_total = Counter(
    'vs_analysis_jobs_total',
    'Total number of analysis jobs started',
    registry=registry
)

analysis_failures_total = Counter(
    'vs_analysis_failures_total',
    'Total number of analysis jobs failed',
    registry=registry
)

analysis_duration_seconds = Histogram(
    'vs_analysis_duration_seconds',
    'Video analysis job duration in seconds',
    buckets=(1, 2, 5, 10, 20, 40, 80, 160, 320, 640, 1280),
    registry=registry
)


def start_timer():
    return time.time()


def observe_latency_ms(t0: float):
    elapsed_ms = (time.time() - t0) * 1000.0
    frame_latency_ms.observe(elapsed_ms)
    return elapsed_ms


def observe_duration_seconds(t0: float):
    return time.time() - t0


def render_metrics():
    return generate_latest(registry)

