# my_sins.py

def s3_log(msg: str):
    """Push a single-line log into S3 immediately.
    (You could buffer inside here or use an upload batch.)
    """


def honeyhive_log(msg: str):
    """Send msg to Opic (whatever API or SDK call).
    """
    # e.g. opic.Client().ingest([msg])
    ...


