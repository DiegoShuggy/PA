from app.metrics_tracker import metrics_tracker

metrics_tracker.track_response_time("test", 0.5, "demo")
metrics_tracker.log_cache_hit()
metrics_tracker.log_user_feedback(3)

print(metrics_tracker.get_performance_stats())
