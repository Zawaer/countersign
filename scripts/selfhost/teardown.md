# Teardown: what to tell the infra agent

Send this once `run_reviews.sh` has finished and `reviews-selfhost/` and `measurement/selfhost.md` are committed:

> The Countersign self-hosted review run on the Verda box (1x A100 80GB, IP <ip>) is done. Please:
> 1. **Shut down and delete the instance**, including its OS volume and any attached storage volume (deleting, not
>    just stopping: a stopped Verda instance still bills its storage, and the disk holds the review contexts).
> 2. Remove the SSH key we used for it from the Verda project if it was added only for this box.
> 3. Reply with the instance's **create and delete times** (or the billed hours) from the Verda console, so the
>    measurement records the real bill, idle time included.

Then, in this container:

```bash
pkill -f 'ssh .*8000:127.0.0.1:8000' || true      # close the tunnel
.venv/bin/python scripts/selfhost/compare.py --repo /data/src/mp --box-hours <billed hours> --gpus 1 --rate 2.39 \
  2234 2283 2129 2297 up-2022 up-1934 up-1967 2234-mut2 2283-mut1 2283-sec1
python3 scripts/sync_numbers.py --check
```

and fill the TODO numbers in `docs/tech-challenges/verda.md` from `measurement/selfhost.md`.

What was on the box, so you know nothing else needs cleaning: `~/selfhost/` (a Python venv with vLLM 0.27.1, the
model weights, `serve.log`, `max_model_len`). The server listened on 127.0.0.1:8000 only; no port was opened, no
secret or token was stored (the model is not gated). The review contexts (MessagePack-CSharp code, open source) only
passed through vLLM's memory (serve.sh does not pass `--enable-log-requests`, so `serve.log` holds no prompt text).
