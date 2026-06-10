import csv
import math
import os
from datetime import datetime, timezone
from celery import shared_task
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.celery_app import celery_app
from app.core.redis_client import cache
from app.core.s3_client import s3_service
from app.crud.competition import submission_crud, leaderboard_crud, competition_crud


@celery_app.task(bind=True)
def evaluate_submission(self, submission_id: int, competition_id: int):
    db: Session = SessionLocal()
    try:
        submission = submission_crud.get(db, id=submission_id)
        if not submission:
            return {"error": "Submission not found"}

        competition = competition_crud.get(db, id=competition_id)
        if not competition:
            return {"error": "Competition not found"}

        self.update_state(state="PROGRESS", meta={"progress": 10, "step": "downloading_submission"})
        submission_path = f"/tmp/sub_{submission_id}.csv"
        try:
            _download_s3_url(submission.submitted_file_url, submission_path)
        except Exception as exc:
            submission.status = "Failed"
            db.add(submission)
            db.commit()
            return {"error": f"Failed to download submission: {exc}"}

        self.update_state(state="PROGRESS", meta={"progress": 30, "step": "downloading_ground_truth"})
        ground_truth_path = f"/tmp/gt_{competition_id}.csv"
        if competition.ground_truth_file_path:
            try:
                _download_s3_url(competition.ground_truth_file_path, ground_truth_path)
            except Exception as exc:
                submission.status = "Failed"
                db.add(submission)
                db.commit()
                return {"error": f"Failed to download ground truth: {exc}"}

        self.update_state(state="PROGRESS", meta={"progress": 50, "step": "calculating_metric"})
        metric = competition.evaluation_metric or "accuracy"
        try:
            score = _calculate_metric(submission_path, ground_truth_path, metric)
        except Exception as exc:
            submission.status = "Failed"
            db.add(submission)
            db.commit()
            return {"error": f"Metric calculation failed: {exc}"}

        self.update_state(state="PROGRESS", meta={"progress": 80, "step": "updating_leaderboard"})

        submission.score = score
        submission.status = "Completed"
        db.add(submission)
        db.commit()

        entry = leaderboard_crud.get_by_user_and_competition(
            db, user_id=submission.user_id, competition_id=competition_id
        )
        if entry:
            if score > (entry.best_score or -float("inf")):
                entry.best_score = score
                db.add(entry)
                db.commit()
        else:
            leaderboard_crud.create(
                db,
                obj_in={"competition_id": competition_id, "user_id": submission.user_id, "best_score": score}
            )

        leaderboard_crud.recalculate_ranks(db, competition_id=competition_id)

        leaderboard_data = leaderboard_crud.get_by_competition(db, competition_id=competition_id)
        cache.set_leaderboard(competition_id, [{"rank": l.rank_position, "score": l.best_score, "user_id": l.user_id} for l in leaderboard_data])
        cache.publish(f"leaderboard:{competition_id}", {"event": "update", "competition_id": competition_id})

        self.update_state(state="SUCCESS", meta={"progress": 100})
        return {"submission_id": submission_id, "score": score}
    finally:
        db.close()


def _download_s3_url(url: str, local_path: str):
    from urllib.parse import urlparse
    parsed = urlparse(url)
    key = parsed.path.lstrip("/")
    if key.startswith(f"{s3_service.bucket}/"):
        key = key[len(f"{s3_service.bucket}/"):]
    s3_service.client.download_file(s3_service.bucket, key, local_path)


def _calculate_metric(pred_path: str, truth_path: str, metric: str) -> float:
    with open(pred_path, "r") as f:
        pred_reader = csv.reader(f)
        pred_header = next(pred_reader, None)
        pred = list(pred_reader)
    with open(truth_path, "r") as f:
        truth_reader = csv.reader(f)
        truth_header = next(truth_reader, None)
        truth = list(truth_reader)

    metric_lower = metric.lower()
    if metric_lower in ("accuracy", "acc"):
        correct = sum(1 for p, t in zip(pred, truth) if p == t)
        return correct / len(truth) if truth else 0.0
    elif metric_lower in ("rmse", "root_mean_squared_error"):
        mse = sum((float(p[0]) - float(t[0])) ** 2 for p, t in zip(pred, truth)) / len(truth)
        return math.sqrt(mse)
    elif metric_lower in ("mae", "mean_absolute_error"):
        return sum(abs(float(p[0]) - float(t[0])) for p, t in zip(pred, truth)) / len(truth)
    elif metric_lower in ("f1", "f1_score"):
        tp = sum(1 for p, t in zip(pred, truth) if p == t and p[0] == "1")
        fp = sum(1 for p, t in zip(pred, truth) if p != t and p[0] == "1")
        fn = sum(1 for p, t in zip(pred, truth) if p != t and t[0] == "1")
        precision = tp / (tp + fp) if (tp + fp) else 0
        recall = tp / (tp + fn) if (tp + fn) else 0
        return 2 * precision * recall / (precision + recall) if (precision + recall) else 0
    else:
        return 0.0
