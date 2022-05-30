import os
import requests
import subprocess
from urllib.parse import urlparse

from cloudevents.sdk.event import v1
from dapr.clients import DaprClient
from dapr.ext.grpc import App
import json
from types import SimpleNamespace
from minio import Minio

app = App()

@app.subscribe(pubsub_name="jetstream-pubsub", topic='request.swinir')
def enhance(event: v1.Event) -> None:
  try:
    data = json.loads(event.Data())
    with DaprClient() as d:
      id = data["id"]
      workdir = os.path.join("/tmp/enhance/", id)
      indir = os.path.join(workdir, "lq")
      outdir = os.path.join(workdir, "results")
      if os.path.isdir(workdir):
        return
      os.makedirs(indir)
      os.makedirs(outdir)

      ix = 0
      for img in data["input"]["images"]:
        with requests.get(img, stream = True) as r:
          u = urlparse(img)
          fn = f'{ix}_{os.path.basename(u.path)}'
          with open(os.path.join(indir, fn), 'wb') as f:
            for chunk in r.iter_content(chunk_size = 16*1024):
              f.write(chunk)
        ix = ix+1

      subprocess.call(['python', 'main_test_swinir.py', '--task', 'real_sr', '--scale', '4', '--large_model', '--model_path', 'model_zoo/swinir/003_realSR_BSRGAN_DFOWMFC_s64w8_SwinIR-L_x4_GAN.pth', '--folder_lq', indir], shell=False)
      client = Minio("dumb.dev", access_key=os.getenv('NIGHTMAREBOT_MINIO_KEY'), secret_key=os.getenv('NIGHTMAREBOT_MINIO_SECRET'))
      results = list()
      for result in os.listdir('results/swinir_real_sr_x4_large'):
        outfile = os.path.join('results/swinir_real_sr_x4_large', result)
        client.fput_object("nightmarebot-output", f"{id}/{result}", outfile, content_type="image/png")
        results.append(result)
        os.remove(outfile)
      d.publish_event(
        pubsub_name="jetstream-pubsub", 
        topic_name="response.swinir", 
        data=json.dumps({
            "id": data["id"], 
            "context": data["context"],
            "images": results}),
        data_content_type="application/json")
  except Exception as e: print(e, flush=True)

app.run(50051)
