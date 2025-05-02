
important!!!!!!! delete all files from github catalog and only leave one - runpod handler and dockerfile, because other files may contain some lines of code that will overwite you model
such as "from pretrained"


Here is a minimal and safe runpod_handler.py file that only checks disk usage on your persistent volume (/runpod-volume). 
It does nothing else, won’t overwrite or touch any files, and won’t interfere with your model or setup.

✅ How to use:
Replace your current runpod_handler.py in GitHub with this one.

It will be deployed to runpod serverless endpoint automatically


Send any test job under "Requests" tab (the input can be anything, e.g., {}). Press RunSync pink button
Put this under the input on left side:



{
  "id": "unique_job_id_123",
  "input": {
    "action": "check_disk"
  }
}


You'll get output showing used space.

